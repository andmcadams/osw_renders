## Master script documentation
    python3 master_script.py
            [-h]                                # Display program help
            --infile INFILE                     # Specify the csv path that contains the render data
            --cache CACHE                       # Specify the directory containing the idx files
            [--outdir OUTDIR]                   # Optional - specify the path of the directory containing the new renders
            [--only-gender {male,female}]       # Optional - specify if you only want male or female renders
            [--render-type {player,chathead}]   # Optional - specify if you only want full equip or chathead renders
            [--id-list ID_LIST]                 # Optional - path to a file with a comma separated list of item ids to render

Unless the `RENDERER_PATH` environment variable is set, the script will look for the renderer at `./renderer-all.jar`

By default, the master script will create male and female equip and chathead renders for every row in the infile that enough data exists for.
These renders will be dumped into a directory named `./renders` and a file of the renamed versions in `./renders_renamed`.
If the `--outdir` option is set, the renders will be placed in the `./[OUTDIR]` and `./[OUTDIR]_renamed` directories.


For example, to generate male chathead renders for a subset of items, you can create a file `ids.txt` with the following content:
```text
26156, 26158, 26160, 26162, 26164, 26166, 26168, 26170, 26172, 26174, 26176, 26178, 26180, 26182
```
and run the following command:
```
python3 master_script.py --infile [INFILE] --cache [CACHE] --only-gender male --render-type chathead --id-list ./ids.txt
```
