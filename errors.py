import requests

resp = requests.get(
    f'https://oldschool.runescape.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:Pages_with_script_errors')

print(resp.json())

