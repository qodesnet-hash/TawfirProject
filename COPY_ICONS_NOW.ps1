# PowerShell Script to Copy Icons and Logo
Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   📱 نقل أيقونات وشعار Tawfir App تلقائياً" -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Set location to project root
Set-Location "C:\Users\mus_2\GitHub\TawfirProject"

# Copy Android Icons
Write-Host "[1/3] نسخ أيقونات Android..." -ForegroundColor Yellow
Write-Host ""

$mipmapFolders = @("mipmap-hdpi", "mipmap-mdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi")
$allIconsOk = $true

foreach ($folder in $mipmapFolders) {
    Write-Host "   → نسخ $folder..." -NoNewline
    
    $source = "AppIcons\android\$folder"
    $destination = "tawfir_app\android\app\src\main\res\$folder"
    
    if (Test-Path $source) {
        try {
            # Create destination if doesn't exist
            if (!(Test-Path $destination)) {
                New-Item -ItemType Directory -Path $destination -Force | Out-Null
            }
            
            # Copy all files
            Copy-Item -Path "$source\*" -Destination $destination -Recurse -Force
            Write-Host " ✅ تم" -ForegroundColor Green
        }
        catch {
            Write-Host " ❌ فشل" -ForegroundColor Red
            $allIconsOk = $false
        }
    }
    else {
        Write-Host " ⚠️  المصدر غير موجود" -ForegroundColor Yellow
        $allIconsOk = $false
    }
}

# Copy Logo
Write-Host ""
Write-Host "[2/3] نسخ الشعار..." -ForegroundColor Yellow
Write-Host ""

# Create images directory if doesn't exist
$imagesDir = "tawfir_app\src\assets\images"
if (!(Test-Path $imagesDir)) {
    New-Item -ItemType Directory -Path $imagesDir -Force | Out-Null
    Write-Host "   ✅ تم إنشاء مجلد images" -ForegroundColor Green
}

# Copy playstore.png as logo.png
Write-Host "   → نسخ playstore.png إلى logo.png..." -NoNewline
try {
    Copy-Item -Path "AppIcons\playstore.png" -Destination "$imagesDir\logo.png" -Force
    Write-Host " ✅ تم" -ForegroundColor Green
}
catch {
    Write-Host " ❌ فشل" -ForegroundColor Red
    $allIconsOk = $false
}

# Copy playstore.png (backup)
Write-Host "   → نسخ playstore.png (نسخة احتياطية)..." -NoNewline
try {
    Copy-Item -Path "AppIcons\playstore.png" -Destination "$imagesDir\playstore.png" -Force
    Write-Host " ✅ تم" -ForegroundColor Green
}
catch {
    Write-Host " ⚠️  فشل (اختياري)" -ForegroundColor Yellow
}

# Copy appstore.png
Write-Host "   → نسخ appstore.png (للاستخدام المستقبلي)..." -NoNewline
try {
    Copy-Item -Path "AppIcons\appstore.png" -Destination "$imagesDir\appstore.png" -Force
    Write-Host " ✅ تم" -ForegroundColor Green
}
catch {
    Write-Host " ⚠️  فشل (اختياري)" -ForegroundColor Yellow
}

# Verify Results
Write-Host ""
Write-Host "[3/3] التحقق من النتائج..." -ForegroundColor Yellow
Write-Host ""

$allOk = $true

# Check Android icons
foreach ($folder in $mipmapFolders) {
    $iconPath = "tawfir_app\android\app\src\main\res\$folder\ic_launcher.png"
    if (Test-Path $iconPath) {
        Write-Host "   ✅ $folder: موجود" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ $folder: ناقص" -ForegroundColor Red
        $allOk = $false
    }
}

# Check logo
if (Test-Path "$imagesDir\logo.png") {
    Write-Host "   ✅ logo.png: موجود" -ForegroundColor Green
}
else {
    Write-Host "   ❌ logo.png: ناقص" -ForegroundColor Red
    $allOk = $false
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($allOk) {
    Write-Host ""
    Write-Host "🎉 ممتاز! تم نسخ جميع الملفات بنجاح!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 الخطوة التالية:" -ForegroundColor Yellow
    Write-Host "   شغّل: SYNC_ICONS.bat لمزامنة التغييرات مع Android"
    Write-Host ""
    Write-Host "🧪 للاختبار:" -ForegroundColor Yellow
    Write-Host "   1. ionic serve - للشعار في Toolbar"
    Write-Host "   2. ionic cap open android - للأيقونات"
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "❌ تحذير: بعض الملفات لم يتم نسخها!" -ForegroundColor Red
    Write-Host "   يرجى التحقق من وجود مجلد AppIcons في المسار الصحيح"
    Write-Host ""
}

Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "اضغط أي مفتاح للإغلاق..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
