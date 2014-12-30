#!/bin/bash

# autopkg automation script which, when run with no arguments, checks current run's output against a default output and sends the output to a user if there are differences

# adjust the following variables for your particular configuration
# you should manually run the script with the initialize option if you change the recipe list, since that will change the output.

autopkg_user="grahamgilbert"

# don't change anything below this line

# define logger behavior
logger="/usr/bin/logger -t autopkg-wrapper"
user_home_dir=`dscl . -read /Users/${autopkg_user} NFSHomeDirectory | awk '{ print $2 }'`

# the git repo containing my overrides. Perform a git clone to get it set up initially.
overrides_dir="${user_home_dir}/src/autopkg-overrides"

# The overrides I use at work
work_list="${overrides_dir}/recipelist.txt"

# The overrides that only apply to my own machines
personal_list="${overrides_dir}/personal-recipes.txt"

# a list of repositories to add to AutoPjg
repo_list="${overrides_dir}/repolist.txt"

# The output list - AutoPkgr uses this
recipe_list="${user_home_dir}/Library/Application Support/AutoPkgr/recipe_list.txt"

function update_repos {
    while IFS= read -r line
    do
        /usr/local/bin/autopkg repo-add $line
    done < $repo_list
}

function merge_recipe_lists {
    cat ${personal_list} > ${recipe_list}
    cat ${work_list} >> ${recipe_list}
}

$logger "starting autopkg to initialize a new default output log"

echo "recipe list: ${recipe_list}"
echo "autopkg user: ${autopkg_user}"
echo "user home dir: ${user_home_dir}"
echo "overrides directory: ${overrides_dir}"
/usr/bin/git -C ${overrides_dir} pull
merge_recipe_lists
update_repos
/usr/local/bin/autopkg repo-update all