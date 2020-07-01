# Nothing (`not`)

Nothing helps coders be more smarter, some cooler, less dumber, and much faster. `not`.

Take hold of the key 🔑 to gradual automation.


## Installation

`nothing-cli` is very young, only an infant. 🐣

If you'd like to give it a try, it's available in alpha on PyPi.

```shell
pip install nothing-cli
```

In part due to its youth, only Python 3.7 and above are supported. 😬


The command for interacting with the tool is `not`. Get the overview of its subcommands like so:

```shell
not --help
```

Get a quick first taste by running:

```python
not sample
```

You should now have a sample Procedure available, aptly named `nothing`. Get an overview of what it does and where it lives with the `describe` subcommand:

```shell
not describe nothing
```

You can invoke it with the `do` subcommand:

```shell
not do nothing
```

You'll be walked through the Procedure for doing... nothing. Enjoy! Folks don't do enough nothing, in my opinion.

## Overview

### A Realistic Example

The central concept of `nothing-cli` is the *Procedure*. A Procedure is simply a `yaml` file in a `.nothing` directory. We interact with them with the `not` command.

Procedures are not quite todo lists, not quite instructions, and not quite forms. The idea is to use them for infrequent, "toilsome" tasks that are easy to get lost in, annoying to document, and hard ––but very enticing–– to automate.

Here's a simple Procedure for a developer's personal checklist before starting work on a new feature branch:

```yaml
---
title: Get started with a feature branch
description: A few preflight checks before you start coding
context:
  - dev_goal: Briefly, what do you want to accomplish with this branch?
  - __feature_branch_name: What name did you come up with for the new branch?
knowns:
  - main_branch: master
steps: |-
  Check out the main branch and get the latest changes:
  git checkout {main_branch} && git pull

  Think of a short, kebab-cased name that captures your goal:
  "{dev_goal}"

  Create the new branch:
  git checkout -b {__feature_branch_name}

  Push the new branch to the remote:
  git push -u {__feature_branch_name}
```

If you copy and paste the above into a file called `preflight-checks.yml` and save it in a directory called `.nothing` (either in your home or working directory), then you can "do" the Procedure by calling:

```shell
not do preflight-checks
```

For those without a terminal handy, it'd look like this:

[![asciicast](https://asciinema.org/a/cbLdJ1QCAhHzOuLsHWwZ4fr0e.svg)](https://asciinema.org/a/cbLdJ1QCAhHzOuLsHWwZ4fr0e)

## Inspo & Rationale

Once upon a time, we all read this article about ["do-nothing scripting"](https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/) by Dan Slimmon.

It's an incredible concept. I've personally wasted hours of my life trying to turn ever-more-complex aliases into [shell functions](https://github.com/ainsleymcgrath/bin/blob/master/.pydev.sh). I've spent days attempting to automate scripts to do extremely infrequent –but highly toilsome– tasks that [probably would not even have taken hours manually](https://github.com/ainsleymcgrath/dotfiles/commit/46add94cb7b5ad068fd7b23fc8305aba85c63762).

"Toil," as Slimmon terms it, sucks. We'll do anything to get away from it. Do-nothing scripts are a place to meet halfway: Nowhere near the cognitive overhead of writing an actual automation script, but more interactive and dynamic than pure documentation.

But, even logic-free & sugary sweet do-nothing scripts are written in the language of your choice can be fragile. Your stylistic decisions rot. There's no formality to creation or maintenance. Hardcoded strings sprinkled on off-the-cuff implementation. Suddenly, toil returns. Utility vanishes.

Realizing this as my team and my friends experimented more with the practice, I did the logical thing: I wrote an entire piece of software to automate the process of writing the code we write to prevent ourselves from writing too much code to automate stuff when we want to stop *toiling* and just write some freaking code.

It's a noble cause, I think. [Insert infrequent terrible process] always goes faster when you can just ask your teammate for that really specific command and copy-paste. Cut them some slack. Get the command from a terminal robot.

### Pudding (The proof is in it)

Here is the original do-nothing script example from Slimmon

```python
import sys

def wait_for_enter():
    raw_input("Press Enter to continue: ")

class CreateSSHKeypairStep(object):
    def run(self, context):
        print("Run:")
        print("   ssh-keygen -t rsa -f ~/{0}".format(context["username"]))
        wait_for_enter()

class GitCommitStep(object):
    def run(self, context):
        print("Copy ~/new_key.pub into the `user_keys` Git repository, then run:")
        print("    git commit {0}".format(context["username"]))
        print("    git push")
        wait_for_enter()

class WaitForBuildStep(object):
    build_url = "http://example.com/builds/user_keys"
    def run(self, context):
        print("Wait for the build job at {0} to finish".format(self.build_url))
        wait_for_enter()

class RetrieveUserEmailStep(object):
    dir_url = "http://example.com/directory"
    def run(self, context):
        print("Go to {0}".format(self.dir_url))
        print("Find the email address for user `{0}`".format(context["username"]))
        context["email"] = raw_input("Paste the email address and press enter: ")

class SendPrivateKeyStep(object):
    def run(self, context):
        print("Go to 1Password")
        print("Paste the contents of ~/new_key into a new document")
        print("Share the document with {0}".format(context["email"]))
        wait_for_enter()

if __name__ == "__main__":
    context = {"username": sys.argv[1]}
    procedure = [
        CreateSSHKeypairStep(),
        GitCommitStep(),
        WaitForBuildStep(),
        RetrieveUserEmailStep(),
        SendPrivateKeyStep(),
    ]
    for step in procedure:
        step.run(context)
    print("Done.")
```

Here it is translated to a `nothing-cli` Procedure:

```yaml
---
title: Provision New User Account
description: Create and distribute an SSH key for a new user.
context:
  - username
  - build_url
  - dir_url
  - email: Copy the new user's email and paste here
steps: |-
  Run:
    ssh-keygen -t rsa -f ~/{username}

  Copy ~/new_key.pub into the `user_keys` Git repository, then run:
    git commit {username}
    git push

  Wait for the build job at {build_url} to finish:

  Go to 1Password
  Paste the contents of ~/new_key into a new document
  Share the document with {email}
```

I know it's impolite to talk about LOC, but the `nothing-cli` procedure version weighs in at 17 to the original 43 (excluding blank lines). The drastically improved readability and editability should speak for itself.

#### Things to Note

You'll notice that context is specified in 2 ways. The first three items are specified using "simple context," where the value is merely a yaml list item. The user is prompted for those values with a default phrase: *Please provide a value for [variable name]*. The last context item uses dictionary syntax, allowing the specification of a friendlier prompt.

Next, the funny looking `|-` next to `steps` specifies a [block scalar](https://yaml-multiline.info/#block-scalars). The very existence of this yaml feature was a great inspiration to create this tool in the first place. It functions as a sort of lawless playground for plain text, supporting:

- Multiline text and indentation.
- A clear visual delineation of content from configuration
- The specification of each step as a paragraph, which is is both obvious to read and easy to edit.

It is worth mentioning, however, that the current version of `nothing-cli` is not able to replicate the original script exactly.

If you run them side-by-side, you'll see that the original uses hard-coded values for `dir_url` and `build_url`. Additionally, the user is prompted for `email` in the middle of the script, rather than at the end. These omissions are discussed in the Planned Features section.

## Planned Features

The alpha version of `nothing-cli` was meant to be as focused as possible. For this reason, some mechanics of the original do-nothing script were omitted.

#### Promptless Knowns & Context

In an ideal world, users could specify context as usual:

```yaml
---
# diet-review.yml
context:
  - favorite_food: What's your favorite thing to eat?
```

But then circumvent the prompt by running the Procedure like this:

```shell
not do diet-review --favorite-food 'french omelet'
```

Even more useful would be specifying a this for knowns:

```yaml
---
# secret-stuff.yml
knowns:
  - secret_password
```

Specifying a known with no value (as a plain yaml list item) would require the Procedure to be run with the value as a command-line option.

```shell
not do secret-stuff # refuses to run
not do secret-stuff --secret_password 'n3veR $h4re tHis--'
```

#### Chaining Procedures

For the composition-minded, it could be a boon to write small, related Procedures and have them run directly into each other, maybe even sharing context.

This could be specified at runtime:

```yaml
not do proc-1 --chain proc-2 --chain proc-3
```

Or in the Procedure itself:

```yaml
---
# use-chains.yml
title: Use chains
description: Demonstration of chain usage
context:
  - name
steps: |-
  Love yourself and your colleagues, {name}.

  Choose composition.
chain:
  to: review-chaining
  pass_context: yes
```

#### Conditional Chaining

We're getting absolutely crazy here, but adding *several* features could allow for supercharged chains:

```yaml
---
# ci-stuff.yml
title: CI/CD Toil
description: Boring CI thing, one day you'll automate. But not now.
context:
  # add syntax for limited choice context
  - deploy_phase[dev/prod]: What kind of deploy are you doing?
chain:
   # use context to determine where chain
  - if:
      deploy_phase_is: dev
      to: dev-deploy
  - if:
      deploy_phase_is: prod
      to: prod-deploy
```

This one is surely a moonshot but damn... I wanna do it 🤩

#### And more!

My head is full of ideas! Perhaps yours is too. If you believe in this tool, drop me a line, I'll be overjoyed and say nice things to you. 😸
