# Nothing (`not`)

Nothing makes coders be more smarter.. `not`.

## What?

Nothing is a tool I devised to formalize the practice of [do-nothing scripting](https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/). The idea is to get the benefits of automation (repeatability, process consolidation) without the drawbacks of writing complex code (time, being 9x or less).

Within the world of Nothing there are 2 main concepts:

### The Task Spec

Blindingly simple to put together with standard yaml. (The funny looking guy `|-` is a called a [block scalar](https://yaml-multiline.info/#block-scalars).)

We'll save this Task Spec in a file called `all-my-work.not`

```yaml
---
title: Set yourself up to be the automation whiz
steps: |-
  Download Nothing by running this:
  pip install not

  Profit. use the `not` command:
  not do [your boring task]
```

A Task Spec can be saved as:

- A `.not` file anywhere local to your cwd. (It's just yaml.)

- A `.yaml` ,`.yml`, or `.not` file in a `~/.nothing` directory or any so-named directory local to your cwd.

***Why "spec"? Isn't it called a do-nothing "script"?***

That's the whole exercise! "Gradual automation."

Scripts are hard. Blocks of plain text are easy. *And* a block of text can be recycled as a blueprint for a script  in the future. When you have time and an *actual* good reason to write that script.

If you're anything like me, you are constantly yearning to write software that writes software for you.

But it's hard.

I've wasted hours of my life trying to turn ever-more-complicated aliases into shell functions, spent days on scripts to do tasks that [probably would not even have taken hours manually](https://github.com/ainsleymcgrath/dotfiles/commit/46add94cb7b5ad068fd7b23fc8305aba85c63762).

It always goes faster when you can just ask your teammmate for that really specific git command and copy paste. Cut them some slack. Get the command from a CLI robot.

### `not`

This easy-on-the-fingers command handles all interactive usage of a Task Spec.

Remember `all-my-work.not`? Run it like this:

```shell
-> not do all-my-work
========================================================
Doing Nothing: Set yourself up to be the automation whiz
========================================================


Step 1:
Download Nothing by running this:
pip install not

Press enter to continue...
```

And so on.

Wanna change it?

```shell
-> not edit all-my-work
# opens the .not file with $EDITOR
```

Want a new one?

```shell
not new preflight-checks
# drops you into your $EDITOR if that's set
```

Didn't like how it turned out? That's fine.

```shell
not drop preflight-checks
```

## There's more! A more dynamic example:

Task specs have [non-negotiably minimal](link-to-rationale.md) support for Python [string formatting](https://docs.python.org/3.8/library/string.html#format-examples).

Any variable name in `context` can be templated into `steps` with `{curly_braces_around_it}`.

```yaml
---
title: A sample set of do-nothing instructions

# the user will be prompted to provide these values
# at the start of the run
context:
  - current_user_name
  - what_user_accomplished_today

# a set of steps is a block scalar
# each step is  denoted as a line break
# plain python templates are used to interpolate context
steps: |-
  Take a good look at yourself, {current_user_name}.

  I heard you accomplished something great today: {what_user_accomplished_today}.
  Give yourself a pat on the back!

# https://yaml-multiline.info/#block-scalars
```

If you'd like, save the above as `sample.yml` and run it like so:

```shell
not do sample
```

## Bigger Example

- Uses dictionary syntax in context
- Uses ternary logic (and maybe expressions?) in steps? ~~Needs to be list-style?~~
- Override global/local config with file-level config

```
---
title: Prepare for a presentation

# the key is the variable, the value is how it's asked for
context:
  - name: What's your name?
  - presentation_topic: What's the topic of your presentation?
  - nervous: Are you feeling nervous about it? (y/n)

# presets are compiled after context, but before steps
presets:
  - calm_down: Take a quick walk, {name}.
  - confidence_booster: Give yourself a pat on the back, {name}!

steps: |-
  { calm_down if nervous else confidence_booster }

  Make bullets for major points if you haven't.

  Find someone to read your notes to. They don't even have to really listen!

  Go slow! The longest pause you can muster is still not long enough to be weird.

config:
  title_prefix: ""
  fine_controls: False
```



## Features

### High config

- project specific `.nothing/_config.yaml` or system `~/.nothing/_config.yaml`
    - One key only: `config:`

- Config options:
    - Title prefix: str
    - Step headers: str
    - Step separators: str
    - Fine controls: bool
    - Coloring (y/n): bool
    - Edit on new: bool

### Some limited support for logic

- specify limited answers to context questions such via suffix of `(answer1/answer2[/...answers])`
- presets get set after context is collected, but the variable names are used in the same way
- they come into play when using ternary or short-circuit expressions*
    - ~~[stretch goal] can expressions include user defined functions? builtins?~~
    - ~~only expressions that take strings; can be passed in unquoted or as variables~~
- [stretch goal] how to link to other task specs...?
    - `linkto` as a key maybe?
    - if context variable names are the same, they'll be passed through?
    - short circuit into them:
        - `{ boolean_var and linkto(other_spec) }`
- [probably not, but] `exit_context` perhaps?
