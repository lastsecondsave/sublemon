import json
import subprocess

from snippets import Icon, generate


def pwsh_cmdlets():
    sources = [
        "Microsoft.PowerShell.Core",
        "Microsoft.PowerShell.Management",
        "Microsoft.PowerShell.Utility",
    ]

    pipeline = [
        "Get-Command",
        f"where Source -IN {','.join(sources)}",
        "select Name, Source",
        "ConvertTo-Json",
    ]

    cmd = ["pwsh", "-NoLogo", "-Command", " | ".join(pipeline)]

    process = subprocess.run(cmd, encoding="utf-8", capture_output=True)

    if process.returncode != 0:
        print("Error: Can't query pwsh for completions.")
        return []

    return [entry["Name"] for entry in json.loads(process.stdout)]


snippets = {"pl": "Write-Output $SEL0"}

completions = {
    ("Cmdlet", Icon.EXTERNAL): pwsh_cmdlets(),
    ("Block", Icon.BLOCK): [
        "begin {}",
        "else {}",
        "end {}",
        "for ($1) {}",
        "function ${1:run} {}",
        "if ($1) {}",
        "param (<=>)",
        "process {}",
        "switch ($1) {}",
    ],
    ("Attribute", Icon.META): [
        ("Parameter", "Parameter"),
    ],
    ("Constant", Icon.CONSTANT): [
        "False",
        "Null",
        "True",
    ],
}

generate("source.powershell", snippets, completions)
