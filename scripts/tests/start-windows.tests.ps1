<#
.SYNOPSIS
    scripts/start-windows.ps1 için senaryo testleri.

.DESCRIPTION
    Betik dot-source ile yüklenir; docker, winget, Start-Process ve indirme
    komutları çağrıları kaydeden sahte fonksiyonlarla değiştirilir. Böylece
    Docker kurulumu dahil tüm akışlar bilgisayarı değiştirmeden denenir.

    Çalıştırma: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\tests\start-windows.tests.ps1
#>
$ErrorActionPreference = 'Stop'
$script:Passed = 0
$script:Failed = 0

. (Join-Path $PSScriptRoot '..\start-windows.ps1')

$OriginalPath = $env:Path
$FakeDesktopExe = Join-Path $env:TEMP 'yanimda-test-docker-desktop.exe'
Set-Content -Path $FakeDesktopExe -Value ''

function Reset-Scenario {
    $global:Calls = New-Object System.Collections.Generic.List[string]
    $global:DockerRunning = $true
    $global:ComposeExit = 0
    $script:DockerDesktopExe = $FakeDesktopExe
    $script:DockerCliDir = Join-Path $env:TEMP 'yanimda-test-yok'
    $script:DockerWaitSeconds = 5
    # Gerçek docker/winget bulunmasın diye PATH sistem klasörüyle sınırlanır.
    $env:Path = Join-Path $env:SystemRoot 'System32'
    Remove-Item -Path Function:winget -Force -ErrorAction SilentlyContinue
    Install-DockerStub
    Install-StartProcessStub
}

function Install-DockerStub {
    function global:docker {
        $global:Calls.Add("docker $args")
        if ($args[0] -eq 'info') { $global:LASTEXITCODE = [int](-not $global:DockerRunning); return }
        if ($args[0] -eq 'compose') { $global:LASTEXITCODE = $global:ComposeExit; return }
        $global:LASTEXITCODE = 0
    }
}

function Remove-DockerStub {
    Remove-Item -Path Function:docker -Force -ErrorAction SilentlyContinue
}

function Install-StartProcessStub {
    function global:Start-Process {
        param($FilePath, $ArgumentList, $Verb, [switch]$Wait, [switch]$PassThru)
        $global:Calls.Add("Start-Process $FilePath $ArgumentList $Verb".Trim())
        if ($FilePath -eq $script:DockerDesktopExe) { $global:DockerRunning = $true }
        if ($FilePath -like '*DockerDesktopInstaller.exe') { Install-DockerStub }
        if ($PassThru) { return [pscustomobject]@{ ExitCode = 0 } }
    }
}

function global:Invoke-WebRequest {
    param($Uri, $OutFile, [switch]$UseBasicParsing)
    $global:Calls.Add("Invoke-WebRequest $Uri")
}

function global:Start-Sleep { param($Seconds) }
function global:Write-Host { }

function Assert-That([string]$Name, [bool]$Condition) {
    if ($Condition) {
        $script:Passed++
        [Console]::WriteLine("  ok   - $Name")
    }
    else {
        $script:Failed++
        [Console]::WriteLine("  FAIL - $Name")
        $global:Calls | ForEach-Object { [Console]::WriteLine("           $_") }
    }
}

function Test-Called([string]$Text) {
    return [bool]($global:Calls | Where-Object { $_ -like "*$Text*" })
}

function Invoke-Scenario([string]$Title, [scriptblock]$Arrange, [hashtable]$Options = @{}) {
    [Console]::WriteLine($Title)
    Reset-Scenario
    & $Arrange
    $script:Failure = $null
    try { Invoke-Main @Options } catch { $script:Failure = $_.Exception.Message }
}

Invoke-Scenario 'Senaryo: Docker kurulu ve çalışıyor' {}
Assert-That 'hatasız biter' ($null -eq $script:Failure)
Assert-That 'compose sıralı başlatılır' (Test-Called 'docker compose up -d --build --wait')
Assert-That 'kurulum yapılmaz' (-not (Test-Called 'winget'))
Assert-That 'site tarayıcıda açılır' (Test-Called 'Start-Process http://localhost:5173')

Invoke-Scenario 'Senaryo: -NoBrowser' {} @{ NoBrowser = $true }
Assert-That 'hatasız biter' ($null -eq $script:Failure)
Assert-That 'tarayıcı açılmaz' (-not (Test-Called 'Start-Process http://localhost:5173'))

Invoke-Scenario 'Senaryo: Docker yok, winget var' {
    Remove-DockerStub
    function global:winget { $global:Calls.Add("winget $args"); Install-DockerStub; $global:LASTEXITCODE = 0 }
}
Assert-That 'hatasız biter' ($null -eq $script:Failure)
Assert-That 'Docker Desktop winget ile kurulur' (Test-Called 'winget install -e --id Docker.DockerDesktop')
Assert-That 'kurulumdan sonra compose çalışır' (Test-Called 'docker compose up -d --build --wait')

Invoke-Scenario 'Senaryo: Docker yok, winget yok' { Remove-DockerStub }
Assert-That 'hatasız biter' ($null -eq $script:Failure)
Assert-That 'resmi kurulum dosyası indirilir' (Test-Called 'Invoke-WebRequest https://desktop.docker.com/win/main/')
Assert-That 'kurulum yönetici onayıyla sessiz çalışır' (Test-Called 'install --quiet --accept-license RunAs')
Assert-That 'kurulumdan sonra compose çalışır' (Test-Called 'docker compose up -d --build --wait')

Invoke-Scenario 'Senaryo: Docker kurulu ama kapalı' { $global:DockerRunning = $false }
Assert-That 'hatasız biter' ($null -eq $script:Failure)
Assert-That 'Docker Desktop başlatılır' (Test-Called "Start-Process $FakeDesktopExe")
Assert-That 'hazır olunca compose çalışır' (Test-Called 'docker compose up -d --build --wait')

Invoke-Scenario 'Senaryo: Docker hiç hazır olmuyor' {
    $global:DockerRunning = $false
    function global:Start-Process { param($FilePath) $global:Calls.Add("Start-Process $FilePath") }
}
Assert-That 'yeniden başlatma önerisiyle hata verir' ($script:Failure -like '*yeniden başlatmanız*')
Assert-That 'compose çalışmaz' (-not (Test-Called 'compose up'))

Invoke-Scenario 'Senaryo: compose başarısız' { $global:ComposeExit = 1 }
Assert-That 'log komutunu öneren hata verir' ($script:Failure -like '*docker compose logs*')
Assert-That 'tarayıcı açılmaz' (-not (Test-Called 'Start-Process http://localhost:5173'))

$env:Path = $OriginalPath
Remove-Item $FakeDesktopExe -ErrorAction SilentlyContinue
[Console]::WriteLine('')
[Console]::WriteLine("Sonuç: $script:Passed geçti, $script:Failed başarısız")
if ($script:Failed -gt 0) { exit 1 }
