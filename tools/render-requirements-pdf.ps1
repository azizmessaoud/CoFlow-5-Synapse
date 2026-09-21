param(
    [string]$InputPath = (Join-Path $PSScriptRoot "..\CoFlow-5_System_Requirements_Book.md"),
    [string]$OutputPath = (Join-Path $PSScriptRoot "..\CoFlow-5_System_Requirements_Book.pdf")
)

$ErrorActionPreference = "Stop"
$inputFull = [System.IO.Path]::GetFullPath($InputPath)
$outputFull = [System.IO.Path]::GetFullPath($OutputPath)
$htmlFull = [System.IO.Path]::ChangeExtension($outputFull, ".print.html")

function Convert-Inline([string]$text) {
    $encoded = [System.Net.WebUtility]::HtmlEncode($text)
    $encoded = [regex]::Replace($encoded, '!\[([^\]]*)\]\(([^)]+)\)', '<span class="image-note">[Image: $1]</span>')
    $encoded = [regex]::Replace($encoded, '\[([^\]]+)\]\(([^)]+)\)', '<a href="$2">$1</a>')
    $encoded = [regex]::Replace($encoded, '`([^`]+)`', '<code>$1</code>')
    $encoded = [regex]::Replace($encoded, '\*\*([^*]+)\*\*', '<strong>$1</strong>')
    $encoded = [regex]::Replace($encoded, '(?<!\*)\*([^*]+)\*(?!\*)', '<em>$1</em>')
    return $encoded
}

$lines = [System.IO.File]::ReadAllLines($inputFull)
$body = New-Object System.Text.StringBuilder
$inCode = $false
$inUl = $false
$inOl = $false
$inTable = $false
$tableHeaderDone = $false

function Close-Blocks {
    if ($script:inUl) { [void]$script:body.AppendLine("</ul>"); $script:inUl = $false }
    if ($script:inOl) { [void]$script:body.AppendLine("</ol>"); $script:inOl = $false }
    if ($script:inTable) { [void]$script:body.AppendLine("</tbody></table>"); $script:inTable = $false; $script:tableHeaderDone = $false }
}

for ($i = 0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]

    if ($line -match '^```') {
        Close-Blocks
        if (-not $inCode) {
            [void]$body.AppendLine("<pre><code>")
            $inCode = $true
        } else {
            [void]$body.AppendLine("</code></pre>")
            $inCode = $false
        }
        continue
    }

    if ($inCode) {
        [void]$body.AppendLine([System.Net.WebUtility]::HtmlEncode($line))
        continue
    }

    if ($line -match '^\|.*\|$') {
        $cells = $line.Trim('|').Split('|') | ForEach-Object { $_.Trim() }
        $isSeparator = ($cells | Where-Object { $_ -notmatch '^:?-{3,}:?$' }).Count -eq 0
        if ($isSeparator) {
            if ($inTable -and -not $tableHeaderDone) {
                [void]$body.AppendLine("</thead><tbody>")
                $tableHeaderDone = $true
            }
            continue
        }
        if (-not $inTable) {
            Close-Blocks
            [void]$body.AppendLine("<table><thead>")
            $inTable = $true
            $tag = "th"
        } else {
            $tag = if ($tableHeaderDone) { "td" } else { "th" }
        }
        [void]$body.AppendLine("<tr>")
        foreach ($cell in $cells) {
            [void]$body.AppendLine("<$tag>$(Convert-Inline $cell)</$tag>")
        }
        [void]$body.AppendLine("</tr>")
        continue
    }

    if ([string]::IsNullOrWhiteSpace($line)) {
        Close-Blocks
        continue
    }

    if ($line -match '^(#{1,6})\s+(.+)$') {
        Close-Blocks
        $level = $matches[1].Length
        [void]$body.AppendLine("<h$level>$(Convert-Inline $matches[2])</h$level>")
        continue
    }

    if ($line -match '^---+$') {
        Close-Blocks
        [void]$body.AppendLine("<hr>")
        continue
    }

    if ($line -match '^>\s?(.*)$') {
        Close-Blocks
        [void]$body.AppendLine("<blockquote>$(Convert-Inline $matches[1])</blockquote>")
        continue
    }

    if ($line -match '^\s*[-*]\s+(.+)$') {
        if ($inOl) { [void]$body.AppendLine("</ol>"); $inOl = $false }
        if (-not $inUl) { Close-Blocks; [void]$body.AppendLine("<ul>"); $inUl = $true }
        [void]$body.AppendLine("<li>$(Convert-Inline $matches[1])</li>")
        continue
    }

    if ($line -match '^\s*\d+\.\s+(.+)$') {
        if ($inUl) { [void]$body.AppendLine("</ul>"); $inUl = $false }
        if (-not $inOl) { Close-Blocks; [void]$body.AppendLine("<ol>"); $inOl = $true }
        [void]$body.AppendLine("<li>$(Convert-Inline $matches[1])</li>")
        continue
    }

    Close-Blocks
    [void]$body.AppendLine("<p>$(Convert-Inline $line)</p>")
}

Close-Blocks
if ($inCode) { [void]$body.AppendLine("</code></pre>") }

$html = @"
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>CoFlow-5 System Requirements Book</title>
<style>
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font-family: "Aptos", "Segoe UI", Arial, sans-serif; color: #172033; font-size: 10pt; line-height: 1.35; }
h1 { color: #123b66; font-size: 24pt; border-bottom: 3px solid #f28c28; padding-bottom: 6pt; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; font-size: 28pt; }
h2 { color: #164f86; font-size: 17pt; margin-top: 20pt; border-bottom: 1px solid #9fb8d0; padding-bottom: 3pt; }
h3 { color: #246394; font-size: 13pt; margin-top: 14pt; }
h4, h5, h6 { color: #365a78; }
p { margin: 5pt 0 8pt 0; }
strong { color: #0e3458; }
a { color: #155fa0; text-decoration: none; }
code { font-family: Consolas, monospace; background: #eef3f7; padding: 1px 3px; }
pre { font-family: Consolas, monospace; font-size: 8pt; background: #f4f6f8; border: 1px solid #c9d4df; padding: 9pt; white-space: pre-wrap; page-break-inside: avoid; }
blockquote { margin: 10pt 15pt; padding: 8pt 12pt; background: #fff5e8; border-left: 4px solid #f28c28; font-style: italic; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 13pt 0; font-size: 8.5pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #164f86; color: white; font-weight: bold; text-align: left; }
th, td { border: 1px solid #8fa6ba; padding: 4pt 5pt; vertical-align: top; }
tr:nth-child(even) td { background: #f3f7fa; }
ul, ol { margin-top: 3pt; margin-bottom: 8pt; }
li { margin-bottom: 3pt; }
hr { border: 0; border-top: 1px solid #9fb8d0; margin: 14pt 0; }
.image-note { color: #6a7280; font-style: italic; }
</style>
</head>
<body>
$($body.ToString())
</body>
</html>
"@

[System.IO.File]::WriteAllText($htmlFull, $html, [System.Text.UTF8Encoding]::new($false))

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($htmlFull, $false, $true)
    $wdExportFormatPDF = 17
    $wdExportOptimizeForPrint = 0
    $doc.ExportAsFixedFormat($outputFull, $wdExportFormatPDF, $false, $wdExportOptimizeForPrint)
} finally {
    if ($doc -ne $null) { $doc.Close($false) }
    if ($word -ne $null) { $word.Quit() }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) 2>$null | Out-Null
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) 2>$null | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$pdf = Get-Item $outputFull
Write-Output ("PDF: {0}" -f $pdf.FullName)
Write-Output ("Bytes: {0}" -f $pdf.Length)
Write-Output ("HTML: {0}" -f $htmlFull)
