# Тестирование API в Windows PowerShell (Invoke-RestMethod)

Ниже — готовые команды для проверки всех основных запросов.

## Базовая настройка

```powershell
# Базовый URL (ваш прод-сервер)
$BaseUrl = "https://sloffy2.pythonanywhere.com"

# Helper: красивые ошибки (чтобы видеть тело ответа при 4xx/5xx)
function Invoke-Api {
    param(
        [Parameter(Mandatory=$true)][string]$Method,
        [Parameter(Mandatory=$true)][string]$Url,
        [Parameter(Mandatory=$false)][hashtable]$Headers = @{},
        [Parameter(Mandatory=$false)]$Body = $null,
        [Parameter(Mandatory=$false)][string]$ContentType = "application/json"
    )

    try {
        if ($null -ne $Body) {
            return Invoke-RestMethod -Method $Method -Uri $Url -Headers $Headers -Body $Body -ContentType $ContentType
        } else {
            return Invoke-RestMethod -Method $Method -Uri $Url -Headers $Headers
        }
    } catch {
        Write-Host "HTTP error:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red

        # Попытаться вытащить тело ответа
        try {
            $resp = $_.Exception.Response
            if ($resp -and $resp.GetResponseStream()) {
                $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
                $text = $reader.ReadToEnd()
                Write-Host "Response body:" -ForegroundColor Yellow
                Write-Host $text
            }
        } catch {}
        throw
    }
}
```

## UC1 — Авторизация (login) и получение текущего пользователя (me)

### Login

```powershell
$loginUrl = "$BaseUrl/api/auth/login"

$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

$login = Invoke-Api -Method POST -Url $loginUrl -Body $loginBody
$token = $login.access_token

$AuthHeaders = @{
    Authorization = "Bearer $token"
}

$login
```

### Me

```powershell
$meUrl = "$BaseUrl/api/auth/me"
$me = Invoke-Api -Method GET -Url $meUrl -Headers $AuthHeaders
$me
```

## Создание пользователя (только admin) — /api/auth/register

```powershell
$registerUrl = "$BaseUrl/api/auth/register"

$registerBody = @{
    username   = "operator1"
    password   = "operator1"
    last_name  = "Оператор"
    first_name = "Иван"
    middle_name = "Иванович"
    role_id    = 2  # ВАЖНО: укажите реальный id роли operator в вашей БД
} | ConvertTo-Json

$newUser = Invoke-Api -Method POST -Url $registerUrl -Headers $AuthHeaders -Body $registerBody
$newUser
```

## UC2/UC3 — Видеорегистраторы (video_recorders)

### Получить список

```powershell
$vrListUrl = "$BaseUrl/api/video-recorders"
$vrs = Invoke-Api -Method GET -Url $vrListUrl -Headers $AuthHeaders
$vrs
```

### Создать (только admin)

```powershell
$vrCreateUrl = "$BaseUrl/api/video-recorders"

$vrCreateBody = @{
    number = "VR-003"
    status = "available"  # available/issued
} | ConvertTo-Json

$vrCreated = Invoke-Api -Method POST -Url $vrCreateUrl -Headers $AuthHeaders -Body $vrCreateBody
$vrCreated

$videoRecorderId = $vrCreated.video_recorder.id
```

### Получить по id

```powershell
$vrGetUrl = "$BaseUrl/api/video-recorders/$videoRecorderId"
$vr = Invoke-Api -Method GET -Url $vrGetUrl -Headers $AuthHeaders
$vr
```

### Обновить (только admin)

```powershell
$vrUpdateUrl = "$BaseUrl/api/video-recorders/$videoRecorderId"

$vrUpdateBody = @{
    status = "available"
} | ConvertTo-Json

$vrUpdated = Invoke-Api -Method PUT -Url $vrUpdateUrl -Headers $AuthHeaders -Body $vrUpdateBody
$vrUpdated
```

### Удалить (только admin; нельзя, если status=issued)

```powershell
$vrDeleteUrl = "$BaseUrl/api/video-recorders/$videoRecorderId"
$vrDeleted = Invoke-Api -Method DELETE -Url $vrDeleteUrl -Headers $AuthHeaders
$vrDeleted
```

## UC4 — Сотрудники (employees)

### Получить список

```powershell
$empListUrl = "$BaseUrl/api/employees"
$employees = Invoke-Api -Method GET -Url $empListUrl -Headers $AuthHeaders
$employees
```

### Создать сотрудника (только admin)

```powershell
$empCreateUrl = "$BaseUrl/api/employees"

$empCreateBody = @{
    full_name = "Иванов Иван Иванович"
    position = "Водитель"
    employee_number = "123456"  # до 6 символов, уникально
} | ConvertTo-Json

$empCreated = Invoke-Api -Method POST -Url $empCreateUrl -Headers $AuthHeaders -Body $empCreateBody
$empCreated

$employeeId = $empCreated.employee.id
```

### Получить сотрудника по id

```powershell
$empGetUrl = "$BaseUrl/api/employees/$employeeId"
$emp = Invoke-Api -Method GET -Url $empGetUrl -Headers $AuthHeaders
$emp
```

### Обновить сотрудника (только admin)

```powershell
$empUpdateUrl = "$BaseUrl/api/employees/$employeeId"

$empUpdateBody = @{
    position = "Старший водитель"
} | ConvertTo-Json

$empUpdated = Invoke-Api -Method PUT -Url $empUpdateUrl -Headers $AuthHeaders -Body $empUpdateBody
$empUpdated
```

### Загрузка фото сотрудника (только admin)

> `Invoke-RestMethod` умеет отправлять multipart/form-data через `-Form`.

```powershell
$photoPath = "C:\temp\photo.jpg"  # поменяйте на реальный путь к файлу
$photoUploadUrl = "$BaseUrl/api/employees/$employeeId/photo"

$photoResp = Invoke-RestMethod -Method POST -Uri $photoUploadUrl -Headers $AuthHeaders -Form @{
    photo = Get-Item $photoPath
}

$photoResp
```

### Скачать фото сотрудника

```powershell
$photoGetUrl = "$BaseUrl/api/employees/$employeeId/photo"
$outPath = "C:\temp\downloaded_photo.jpg"

Invoke-WebRequest -Uri $photoGetUrl -Headers $AuthHeaders -OutFile $outPath
Get-Item $outPath
```

### Удалить сотрудника (только admin)

```powershell
$empDeleteUrl = "$BaseUrl/api/employees/$employeeId"
$empDeleted = Invoke-Api -Method DELETE -Url $empDeleteUrl -Headers $AuthHeaders
$empDeleted
```

## UC5/UC6/UC7 — Выдача/Возврат/История (issues)

### Выдать видеорегистратор сотруднику (UC5)

```powershell
$issueUrl = "$BaseUrl/api/issues/issue"

$issueBody = @{
    video_recorder_id = $videoRecorderId
    employee_id = $employeeId
} | ConvertTo-Json

$issued = Invoke-Api -Method POST -Url $issueUrl -Headers $AuthHeaders -Body $issueBody
$issued
```

### Активные выдачи (issued) (доп. эндпоинт)

```powershell
$activeUrl = "$BaseUrl/api/issues/active"
$active = Invoke-Api -Method GET -Url $activeUrl -Headers $AuthHeaders
$active
```

### История (UC7)

```powershell
$historyUrl = "$BaseUrl/api/issues/history"
$historyAll = Invoke-Api -Method GET -Url $historyUrl -Headers $AuthHeaders
$historyAll

# История по видеорегистратору
$historyVrUrl = "$BaseUrl/api/issues/history?video_recorder_id=$videoRecorderId"
$historyVr = Invoke-Api -Method GET -Url $historyVrUrl -Headers $AuthHeaders
$historyVr

# История по сотруднику
$historyEmpUrl = "$BaseUrl/api/issues/history?employee_id=$employeeId"
$historyEmp = Invoke-Api -Method GET -Url $historyEmpUrl -Headers $AuthHeaders
$historyEmp
```

### Возврат видеорегистратора (UC6)

```powershell
$returnUrl = "$BaseUrl/api/issues/return"

$returnBody = @{
    video_recorder_id = $videoRecorderId
    employee_id = $employeeId
} | ConvertTo-Json

$returned = Invoke-Api -Method POST -Url $returnUrl -Headers $AuthHeaders -Body $returnBody
$returned
```

## Быстрая проверка / и /api/health

```powershell
Invoke-Api -Method GET -Url "$BaseUrl/"
Invoke-Api -Method GET -Url "$BaseUrl/api/health"
```


