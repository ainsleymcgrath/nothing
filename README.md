# Nothing (`not`)

Nothing help coder be more smarter, some cooler, less dumber. `not`.

## Inspo & Rationale

Once upon a time we all read this brief article about ["do-nothing scripting"](https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/).

Very cool, but even those scripts take time!

[Juxtapose OG example against Recipe version]

More why:

- Ease automation woes (dotfile scripts lol). Clip your wax wings early before you try to build robots.
- Fast to use! Build these things rampantly at the project level
    - Attach them to commit hooks?
    - Keep yourself accountable
    - Bring consistency to things u do often
- Shareable

## Sample

Configure your Recipe as simple yaml mixed with simple Python templating:

```yaml
---
title: A sample set of do-nothing instructions

# the user will be prompted to provide these values
# and the values will persist through the run
context:
  - current_user_name
  - what_user_accomplished_today

# a set of steps is most easily represented as block scalar
# each step is simply denoted as a line break
# plain python templates are used to interpolate context
steps: |-
  Take a good look at yourself, {current_user_name}.

  I heard you accomplished something great today: {what_user_accomplished_today}.
  Give yourself a pat on the back!

# https://yaml-multiline.info/#block-scalars
```

Run it like so:

```shell
not do sample
```

Want a new one?

```shell
not new preflight-checks
# drops you into your $EDITOR if that's set
```

Didn't like how it turned out? That's fine.

```shell
not edit preflight-checks
```

## Bigger Example

- Uses dictionary syntax in context
- Higher config

## Features

### Stylish & Modern

- Pleasant interactivity a-la the Nicest CLI tools
- Colorful & playful since `work_smart == work_less == play_more`
- Funky (but standard), highly readable YAML format
- High config
    - (Give much more thought to where how & when)

### Saving your sweet nothings

- Can be in a project-specific `.nothing/` directory
- or system level `~/.nothing`
- or as a local `*.not` file
