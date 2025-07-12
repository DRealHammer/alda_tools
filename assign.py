from os import listdir, chdir, mkdir, rename
from argparse import ArgumentParser

def get_submission_names(filename):
    team = filename.split('-20')[0]
    names = team.split('__')

    return names

# match as good as possible
# assume a 0/1 to 0/1 relation: you can submit a sec_file but not a main_file
# you can also submit both
# returns a association of relations between files or None as partner if none found
def fuzzy_match(main_files, sec_files):
    main_names = [(fn.split('-20')[0], fn) for fn in main_files]
    main_teams = [(tn.split('__'), fn) for tn, fn in main_names]

    sec_names = [(fn.split('-20')[0], fn) for fn in sec_files]
    sec_teams = [(tn.split('__'), fn) for tn, fn in sec_names]

    # relation between (x, y)
    # x main file
    # y secondary file
    associations = []

    unmatched_main = main_teams.copy()
    unmatched_sec = sec_teams.copy()

    # for every main_file find a secondary file to match with
    for team, main_file in main_teams:
        match = None
        # try it with every member
        for member in team:

            # go through every possible team
            for sec_team, sec_file in unmatched_sec:

                # member is in a secondary team as well -> this is the corresponding team
                if member in sec_team:
                    match = sec_file
                    associations.append((main_file, match))
                    unmatched_main.remove((team, main_file))
                    unmatched_sec.remove((sec_team, sec_file))
                    break

            if match is not None:
                break

        if match is None:
            #print(f'no match for team {main_file}')
            pass

    print(f'=> Found {len(associations)} connections and added them')
    print(f'=> Found {len(unmatched_main) if len(unmatched_main) > 0 else "no"} primary loose ends')
    print(f'=> Found {len(unmatched_sec) if len(unmatched_sec) > 0 else "no"} secondary loose ends')

    if len(unmatched_sec) > 0 and len(unmatched_main) > 0:
        print('WARNING: Not all submissions could be matched. As there are possible matches left, check the respective folders and manually match if desired')
        print('WARNING: Following submissions could not be matched:')

        if len(unmatched_main) > 0:
            print('Primary Submissions:')
            for t in unmatched_main:
                print(f'\t{t[1]}')
        if len(unmatched_sec) > 0:
            print('Secondary Submissions:')
            for t in unmatched_sec:
                print(f'\t{t[1]}')
    for team, fn in unmatched_main:
        associations.append((fn, None))
    for team, fn in unmatched_sec:
        associations.append((None, fn))

    return associations

parser = ArgumentParser(
    prog='assign.py',
    description='Splits up the number of files and directories into 4 different directories as evenly as possible. For safety reasons the directory needs to be provided.',
    )

parser.add_argument('submissions', help='Main Folder of the submission to split up')
parser.add_argument('-f', '--feedback_dir', help='Optional Folder of feedback for every main submission, will be fuzzy matched by Mampf Names')
parser.add_argument('-n', '--number', default=4, help="Number of Tutors the submissions will be split for")
parser.add_argument('-o', '--output', default='tutor_assignments', help="Foldername of the final destination of the submissions")
parser.add_argument('-c', action='store_true', help="Optional CSV of the names for every tutor of this assignment")

args = parser.parse_args()

#print(args)

create_csv = args.c

sub_dir = args.submissions
feedback_dir = args.feedback_dir

NUM_TUTOR = args.number
OUTPUT_NAME = args.output

# create output folder for all data
try:
    mkdir(OUTPUT_NAME)
except FileExistsError:
    pass


# load lists of files in two directories
files = listdir(sub_dir)

# create relational list for case feedback or no feedback
if feedback_dir is None:
    connections = [(f, None) for f in files]
else:
    feedback_files = listdir(feedback_dir)

    # fuzzy match
    connections = fuzzy_match(feedback_files, files)


# create subdir for every submission team, move all files in there
for fb, sub in connections:

    # only single zip file is present -> move the file and go to the next
    if fb is None:
        rename(f'{sub_dir}/{sub}', f'{OUTPUT_NAME}/{sub}')
        continue
    elif sub is None:
        rename(f'{feedback_dir}/{fb}', f'{OUTPUT_NAME}/{fb}')
        continue

    # we have both files
    # per default use feedback as folder name as uploads are usually here
    subfolder_name = fb

    # cut away the .zip and create a folder that will have the correct name for batch upload
    subfolder_name = subfolder_name[:-4]
    subfolder = f'{OUTPUT_NAME}/{subfolder_name}'
    mkdir(subfolder)

    # now move both files into the folder
    rename(f'{sub_dir}/{sub}', f'{subfolder}/{sub}')
    rename(f'{feedback_dir}/{fb}', f'{subfolder}/{fb}')


# now assign the submissions to tutors
chdir(OUTPUT_NAME)

folder_names = [f'assign_{i + 1}' for i in range(NUM_TUTOR)]
for name in folder_names:
    try:
        mkdir(f'{name}')
    except FileExistsError:
        print(f'Folder {name} already exists, skipping...')

submits = listdir()
for name in folder_names:
    submits.remove(name)

submits.sort()

per_tutor = len(submits) // NUM_TUTOR
rest = len(submits) % NUM_TUTOR

num_per_tutor = [per_tutor] * NUM_TUTOR
for i in range(rest):
    num_per_tutor[i] += 1


assignment = []
current = 0
for n in num_per_tutor:
    following = current + n
    assignment.append(submits[current:following])
    current = following

for folder, tutor_assignments in zip(folder_names, assignment):
    for submission in tutor_assignments:
        rename(submission, f'{folder}/{submission}')


if create_csv:
    with open("assignment.csv", '+w') as file:

        file.write("Tutor,Student\n")
        for folder, tutor_assignments in zip(folder_names, assignment):
            for submission in tutor_assignments:
                names = get_submission_names(submission)

                for name in names:
                    file.write(f'{folder},{name}\n')
