import sys
import yaml

import typer

app = typer.Typer()


from .theatrics import dramatic_title, spacious_print


class Step:
    def __init__(self, prompt, **template_vars):
        self.prompt = prompt
        self.template_vars = template_vars

    def do(self):
        try:
            spacious_print(self.prompt.format(**self.template_vars))
        except KeyError:
            spacious_print(self.prompt)


@app.command()
def heee(instructions_document: str):

    with open(f"{instructions_document}.yml") as f:
        yml = yaml.full_load(f.read())

        title = yml["title"]
        context_dict = {}

        dramatic_title(f"Doing nothing: {title}")

        if "context" in yml:
            for context_var in yml["context"]:
                context_value = input(f"Please provide a value for {context_var}\n")
                context_dict[context_var] = context_value
                print()

        steps = [Step(prompt, **context_dict) for prompt in yml["steps"].split("\n\n")]

        for i, step in enumerate(steps):
            print(f"Step {i + 1}:")
            step.do()

        print("\nDone!")
