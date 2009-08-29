from optparse import OptionParser
import os
import subprocess

supported_scm_repositories = {'.git': ('git', 'pull'),
                            '.hg': (('hg', 'pull'),
                                    ('hg', 'update')),
                            '.svn': ('svn', 'update')}

def main():
    parser = OptionParser(usage='Usage: %prog parent_directory')
    parser.add_option('--dry-run', action='store_true', help='display the actions that will be undertaken without actually executing them')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('the parent directory must be supplied as the only positional argument.')
    parent_directory = args[0]
    run(parent_directory, options.dry_run)

def run(parent_directory, dry_run):
    scm_directories = dict()
    # Walk through the parent directory hierarchy to find repository directories
    for root, child_directories, child_files in os.walk(parent_directory):
        processed_scm_dirs = flatten(scm_directories.values())
        current_scm_dirs = [directory for directory in child_directories if directory in supported_scm_repositories.keys()]
        for scm in current_scm_dirs:
            # Make sure we don't go deeper than the first level where we found the repository directory
            if [scm_dir for scm_dir in processed_scm_dirs if root.startswith(scm_dir)]:
                continue
            if scm not in scm_directories:
                scm_directories[scm] = []
            scm_directories[scm] += [root]
    # Get the commands to run, then update everything, one SCM at a time
    for scm, directories in scm_directories.iteritems():
        scm_commands = supported_scm_repositories[scm]
        for directory in directories:
            commands_to_run = []
            for scm_command in scm_commands:
                if isinstance(scm_command, tuple):
                    commands_to_run += [scm_command]
                else:
                    commands_to_run += [scm_commands]
                    break
            for command_to_run in commands_to_run:
                subprocess.call(['echo', "Calling '%s' in directory '%s'." % (' '.join(command_to_run), directory)])
                if not dry_run:
                    subprocess.call(command_to_run, cwd=directory)
                    subprocess.call('echo')

# Function taken from http://www.daniel-lemire.com/blog/archives/2006/05/10/flattening-lists-in-python/
def flatten(l):
    """Flattens a multidimensional list into a unidimensional list."""
    if isinstance(l,list):
        return sum(map(flatten,l),[])
    else:
        return [l]

if __name__ == "__main__":
    main()
