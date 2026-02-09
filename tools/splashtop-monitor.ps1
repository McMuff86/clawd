# ============================================================
# Splashtop Monitor v2 - Erkennt und loggt Fernzugriffe
# ============================================================
#
# Starten:  powershell -ExecutionPolicy Bypass -File splashtop-monitor.ps1
# Minimiert starten:  
#   powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File splashtop-monitor.ps1
# Stoppen:  Ctrl+C oder Task-Manager
#
# Log: %USERPROFILE%\Desktop\splashtop-log.csv

param(
    [int]$Interval = 10,           # Prüf-Intervall in Sekunden
    [switch]$Toast,                 # Windows Toast-Benachrichtigung bei Zugriff
    [switch]$Hidden                 # Fenster verstecken
)

# --- Config ---
$LogFile = "$env:USERPROFILE\Desktop\splashtop-log.csv"
$SplashtopLogDir = "$env:ProgramFiles\Splashtop\Splashtop Remote\Server\log"  # Splashtop eigene Logs
$SplashtopProcessNames = @("SRService", "SRAgent", "SRFeature", "SRManager", "SRStreamer", "strwinclt")

# --- Init ---
if (-not (Test-Path $LogFile)) {
    "Timestamp,Event,Severity,Details" | Out-File $LogFile -Encoding UTF8
}

# State tracking
$state = @{
    ServiceStatus    = $null
    ActiveSession    = $false
    SessionStart     = $null
    Connections      = @()
    LastTrafficBytes = @{}
    LastEventLogCheck = (Get-Date)
}

# --- Functions ---
function Write-Log($Event, $Details, $Severity = "INFO") {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    # CSV escapen
    $safeDetails = $Details -replace '"', '""'
    "$ts,$Event,$Severity,`"$safeDetails`"" | Out-File $LogFile -Append -Encoding UTF8
    
    $color = switch ($Severity) {
        "ALERT"   { "Red" }
        "WARNING" { "Yellow" }
        "INFO"    { "Cyan" }
        default   { "Gray" }
    }
    Write-Host "[$ts] [$Severity] $Event - $Details" -ForegroundColor $color
}

function Show-Toast($Title, $Message) {
    if (-not $Toast) { return }
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        $template = @"
<toast>
    <visual><binding template="ToastText02">
        <text id="1">$Title</text>
        <text id="2">$Message</text>
    </binding></visual>
    <audio src="ms-winstores-app-notification" />
</toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Splashtop Monitor")
        $notifier.Show([Windows.UI.Notifications.ToastNotification]::new($xml))
    } catch {}
}

function Get-SplashtopProcesses {
    Get-Process | Where-Object {
        $name = $_.ProcessName.ToLower()
        ($SplashtopProcessNames | ForEach-Object { $_.ToLower() }) -contains $name -or
        $name -like "*splashtop*"
    }
}

function Get-SplashtopConnections {
    $result = @()
    $procs = Get-SplashtopProcesses
    foreach ($proc in $procs) {
        try {
            $conns = Get-NetTCPConnection -OwningProcess $proc.Id -ErrorAction SilentlyContinue |
                Where-Object { 
                    $_.State -eq "Established" -and 
                    $_.RemoteAddress -ne "127.0.0.1" -and 
                    $_.RemoteAddress -ne "::1" -and
                    $_.RemoteAddress -ne "0.0.0.0"
                }
            foreach ($conn in $conns) {
                # DNS Reverse Lookup (cached)
                $hostname = try { [System.Net.Dns]::GetHostEntry($conn.RemoteAddress).HostName } catch { $conn.RemoteAddress }
                
                $result += [PSCustomObject]@{
                    Process    = $proc.ProcessName
                    PID        = $proc.Id
                    RemoteIP   = $conn.RemoteAddress
                    RemoteHost = $hostname
                    RemotePort = $conn.RemotePort
                    LocalPort  = $conn.LocalPort
                    State      = $conn.State
                }
            }
        } catch {}
    }
    return $result
}

function Check-WindowsEventLog {
    # Prüfe Windows Security/System Event Log auf Remote-Logons seit letztem Check
    try {
        # Event ID 4624 = Successful Logon, Logon Type 10 = RemoteInteractive (RDP)
        # Event ID 4778 = Session Reconnected
        # Event ID 4779 = Session Disconnected
        $events = Get-WinEvent -FilterHashtable @{
            LogName   = 'Security'
            Id        = 4624, 4778, 4779
            StartTime = $state.LastEventLogCheck
        } -ErrorAction SilentlyContinue

        foreach ($evt in $events) {
            $msg = $evt.Message -split "`n" | Select-Object -First 3 | ForEach-Object { $_.Trim() }
            $summary = $msg -join " | "
            
            if ($evt.Id -eq 4624 -and $evt.Message -match "Logon Type:\s+10") {
                Write-Log "REMOTE_LOGON" "Windows Remote-Logon erkannt: $summary" "ALERT"
                Show-Toast "⚠️ Remote Logon!" "Jemand hat sich remote eingeloggt"
            }
            elseif ($evt.Id -eq 4778) {
                Write-Log "SESSION_RECONNECT" "Session wiederverbunden: $summary" "WARNING"
            }
            elseif ($evt.Id -eq 4779) {
                Write-Log "SESSION_DISCONNECT" "Session getrennt: $summary" "INFO"
            }
        }
    } catch {}
    
    $state.LastEventLogCheck = Get-Date
}

function Check-SplashtopLogs {
    # Splashtop eigene Logfiles nach Verbindungen durchsuchen
    if (-not (Test-Path $SplashtopLogDir)) { return }
    
    try {
        $recentLogs = Get-ChildItem $SplashtopLogDir -Filter "*.log" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-2) }
        
        foreach ($log in $recentLogs) {
            $newLines = Get-Content $log.FullName -Tail 20 -ErrorAction SilentlyContinue |
                Where-Object { $_ -match "connect|session|auth|login|remote|viewer" }
            
            foreach ($line in $newLines) {
                Write-Log "SPLASHTOP_LOG" "$($log.Name): $line" "WARNING"
            }
        }
    } catch {}
}

function Measure-NetworkTraffic {
    # Netzwerk-Traffic pro Splashtop-Prozess messen
    $procs = Get-SplashtopProcesses
    foreach ($proc in $procs) {
        try {
            $key = $proc.ProcessName
            $currentIO = $proc.GetType().GetProperty('TotalProcessorTime') # Fallback
            
            # Arbeite mit IO Counters wenn verfügbar
            $ioRead = 0; $ioWrite = 0
            try {
                # .NET Process IO
                $perf = Get-Counter "\Process($($proc.ProcessName))\IO Data Bytes/sec" -ErrorAction SilentlyContinue
                if ($perf) {
                    $bytesPerSec = [math]::Round($perf.CounterSamples[0].CookedValue / 1KB, 1)
                    if ($bytesPerSec -gt 50) {  # Mehr als 50 KB/s = verdächtig (Bildschirm-Streaming)
                        Write-Log "HIGH_TRAFFIC" "$key: $bytesPerSec KB/s - Mögliches Bildschirm-Streaming!" "ALERT"
                        Show-Toast "⚠️ Splashtop Traffic!" "$bytesPerSec KB/s - Möglicher Fernzugriff"
                        
                        if (-not $state.ActiveSession) {
                            $state.ActiveSession = $true
                            $state.SessionStart = Get-Date
                            Write-Log "SESSION_START" "Fernzugriff-Session erkannt (Traffic: $bytesPerSec KB/s)" "ALERT"
                        }
                    } elseif ($bytesPerSec -lt 10 -and $state.ActiveSession) {
                        $duration = (Get-Date) - $state.SessionStart
                        Write-Log "SESSION_END" "Fernzugriff-Session beendet. Dauer: $([math]::Round($duration.TotalMinutes,1)) Minuten" "WARNING"
                        $state.ActiveSession = $false
                        $state.SessionStart = $null
                    }
                }
            } catch {}
        } catch {}
    }
}

# --- Main Loop ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Splashtop Monitor v2" -ForegroundColor Cyan
Write-Host "  Log: $LogFile" -ForegroundColor Gray
Write-Host "  Intervall: ${Interval}s" -ForegroundColor Gray
Write-Host "  Toast: $Toast" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "MONITOR_START" "Splashtop Monitor v2 gestartet (Intervall: ${Interval}s, Toast: $Toast)"

while ($true) {
    try {
        # 1. Service-Status
        $services = Get-Service | Where-Object { $_.DisplayName -like "*Splashtop*" }
        foreach ($svc in $services) {
            if ($svc.Status -ne $state.ServiceStatus) {
                $severity = if ($svc.Status -eq "Running") { "WARNING" } else { "INFO" }
                Write-Log "SERVICE_CHANGE" "$($svc.DisplayName): $($state.ServiceStatus) -> $($svc.Status)" $severity
                $state.ServiceStatus = $svc.Status
            }
        }

        # 2. Netzwerkverbindungen
        $currentConns = Get-SplashtopConnections
        $currentKeys = $currentConns | ForEach-Object { "$($_.RemoteIP):$($_.RemotePort)" }
        $lastKeys = $state.Connections | ForEach-Object { "$($_.RemoteIP):$($_.RemotePort)" }

        # Neue Verbindungen
        foreach ($conn in $currentConns) {
            $key = "$($conn.RemoteIP):$($conn.RemotePort)"
            if ($key -notin $lastKeys) {
                Write-Log "NEW_CONNECTION" "$($conn.Process) (PID $($conn.PID)) -> $($conn.RemoteHost) ($($conn.RemoteIP):$($conn.RemotePort))" "ALERT"
                Show-Toast "🔴 Splashtop Verbindung!" "Neue Verbindung zu $($conn.RemoteHost)"
            }
        }

        # Geschlossene Verbindungen
        foreach ($conn in $state.Connections) {
            $key = "$($conn.RemoteIP):$($conn.RemotePort)"
            if ($key -notin $currentKeys) {
                Write-Log "CONNECTION_CLOSED" "$($conn.Process) -> $($conn.RemoteHost) ($($conn.RemoteIP):$($conn.RemotePort))" "INFO"
            }
        }

        $state.Connections = $currentConns

        # 3. Traffic messen
        Measure-NetworkTraffic

        # 4. Windows Event Log (alle 60s)
        if (((Get-Date) - $state.LastEventLogCheck).TotalSeconds -ge 60) {
            Check-WindowsEventLog
        }

        # 5. Splashtop eigene Logs (alle 30s)
        Check-SplashtopLogs

    } catch {
        Write-Log "ERROR" $_.Exception.Message "WARNING"
    }

    Start-Sleep -Seconds $Interval
}
