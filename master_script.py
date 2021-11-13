import argparse

import create_renders
import rename_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to generate renders')
    parser.add_argument('--cache', required=True, help='Path to the cache to use')
    parser.add_argument('--outdir', default='renders', help='Folder to use for the renderer output')
    parser.add_argument('--only-gender', choices=['male', 'female'],
                        help='Only generate renders for the given gender. Defaults to generating both.')
    parser.add_argument('--render-type', choices=['player', 'chathead'],
                        help='Only generate renders for the given type. Defaults to generating both.')
    parser.add_argument('--id-list', help='Only generate renders for the ids in this file (comma separated list)')
    args = parser.parse_args()

    infile = args.infile
    cache = args.cache
    outdir = args.outdir
    only_gender = args.only_gender
    only_render = args.render_type
    only_ids_file = args.id_list

    rendering_valid = create_renders.validate_args(infile, cache, outdir, only_ids_file)
    renaming_valid = rename_files.validate_args(infile, outdir, only_ids_file, check_renders_dir=False)
    if not rendering_valid or not renaming_valid:
        exit(1)

    # Note that the renders_dir for renaming is the outdir for rendering
    create_renders.start_up(infile, cache, outdir, only_gender, only_render, only_ids_file)
    rename_files.start_up(infile, outdir, None, only_gender, only_render, only_ids_file)


if __name__ == '__main__':
    main()
