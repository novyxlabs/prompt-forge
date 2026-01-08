#!/usr/bin/env python3
"""Prompt Forge - Craft and test AI prompts locally"""

import sys, json, re, argparse
from datetime import datetime
from pathlib import Path

VERSION = "1.0.0"
DEFAULT_RULES = [
    {"regex": r"code|programming|python|javascript|function|class|implement", 
     "response": "Here's a code implementation:\n\n```\n# Implementation\n```\n\nThis demonstrates the functionality."},
    {"regex": r"explain|what is|describe|definition",
     "response": "Explanation:\n\nKey points:\n1. First\n2. Second\n3. Third"},
    {"regex": r"list|enumerate|steps|how to",
     "response": "Steps:\n\n1. First\n2. Second\n3. Third"},
    {"regex": r"debug|error|fix|problem",
     "response": "Troubleshooting:\n\n**Problem:** [issue]\n**Solution:** [fix]\n**Explanation:** [why]"},
    {"regex": r"review|analyze|evaluate",
     "response": "Analysis:\n\n**Strengths:** Point 1\n**Improvements:** Point 2"},
    {"regex": r".*", "response": "I understand. Here's a response addressing your needs."}
]

def main():
    try:
        args = parse_args()
        if args.version: return print(f"prompt-forge v{VERSION}")
        template = load_template(args)
        variables = extract_variables(template)
        if args.check:
            print("Template variables:")
            for var, default in variables.items():
                status = f'(default: "{default}")' if default else '(required)'
                print(f"  - {var} {status}")
            return
        values = collect_values(variables, args)
        rendered = render_template(template, values)
        if args.dry_run: return print("=== DRY RUN ===\n" + rendered)
        response = simulate_response(rendered, load_rules(args.rules) if args.rules else DEFAULT_RULES, values) if args.simulate else None
        format_output(rendered, response, args)
        if args.save: save_to_history(rendered, response, args.save)
    except KeyboardInterrupt: sys.exit(1)
    except Exception as e: print(f"Error: {e}", file=sys.stderr); sys.exit(1)

def parse_args():
    p = argparse.ArgumentParser(description="Craft and test AI prompts locally")
    p.add_argument('template', nargs='?', help="Template file (or stdin)")
    p.add_argument('--var', action='append', default=[], metavar='K=V', help="Variable")
    p.add_argument('--vars', metavar='FILE', help="JSON variables")
    p.add_argument('--interactive', action='store_true', help="Prompt for missing")
    p.add_argument('--template', dest='inline_template', metavar='TEXT', help="Inline template")
    p.add_argument('--simulate', action='store_true', help="Simulate response")
    p.add_argument('--rules', metavar='FILE', help="Custom rules")
    p.add_argument('--format', choices=['text','markdown','json'], default='text')
    p.add_argument('--show-tokens', action='store_true', help="Token estimate")
    p.add_argument('--save', nargs='?', const=str(Path.home()/'.prompt-forge.log'), metavar='FILE')
    p.add_argument('--check', action='store_true', help="List variables")
    p.add_argument('--dry-run', action='store_true', help="Preview")
    p.add_argument('--version', action='store_true', help="Version")
    args = p.parse_args()
    if args.inline_template and args.template: p.error("Cannot specify both file and --template")
    if args.check and (args.simulate or args.save): p.error("Cannot combine --check with actions")
    return args

def load_template(args):
    if args.inline_template: return args.inline_template
    elif args.template:
        with open(args.template, 'r') as f: return f.read()
    else:
        if sys.stdin.isatty(): raise ValueError("No template (use file, --template, or stdin)")
        return sys.stdin.read()

def extract_variables(template):
    return {name: default or None for name, default in re.findall(r'{{(\w+)(?:\|default="([^"]*)")?}}', template)}

def collect_values(variables, args):
    values = {}
    if args.vars:
        with open(args.vars, 'r') as f: values.update(json.load(f))
    for v in args.var:
        if '=' not in v: raise ValueError(f"Invalid --var: {v} (use KEY=VALUE)")
        k, val = v.split('=', 1)
        values[k] = val
    for var, default in variables.items():
        if var not in values and default: values[var] = default
    if args.interactive:
        for var in variables:
            if var not in values:
                default = variables[var]
                val = input(f"Enter '{var}'" + (f" [{default}]" if default else "") + ": ").strip()
                values[var] = val if val else (default or "")
    missing = [v for v in variables if v not in values]
    if missing: raise ValueError(f"Missing: {', '.join(missing)}")
    unused = [v for v in values if v not in variables]
    if unused: print(f"Warning: Unused: {', '.join(unused)}", file=sys.stderr)
    return values

def render_template(template, values):
    result = template
    for var, val in values.items():
        result = re.sub(r'{{' + re.escape(var) + r'(?:\|default="[^"]*")?}}', str(val), result)
    return result

def load_rules(filepath):
    with open(filepath, 'r') as f: return json.load(f).get('rules', [])

def simulate_response(prompt, rules, values):
    for rule in rules:
        if re.search(rule['regex'], prompt, re.IGNORECASE):
            resp = rule['response']
            for var, val in values.items(): resp = resp.replace(f'{{{{{var}}}}}', str(val))
            return resp
    return "No matching response."

def estimate_tokens(text): return int(len(text.split()) * 1.3)

def format_output(prompt, response, args):
    tokens = estimate_tokens(prompt) if args.show_tokens else None
    if args.format == 'json':
        out = {"prompt": prompt, "timestamp": datetime.now().isoformat()}
        if tokens: out['tokens'] = tokens
        if response: out['response'] = response
        print(json.dumps(out, indent=2))
    elif args.format == 'markdown':
        print(f"# Prompt\n\n{prompt}")
        if tokens: print(f"\n## Metadata\n- Tokens: {tokens}\n- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if response: print(f"\n# Simulated Response\n\n{response}")
    else:
        print(prompt)
        if tokens: print(f"\n[Tokens: {tokens}]")
        if response: print(f"\n---\n{response}")

def save_to_history(prompt, response, filepath):
    fp = Path(filepath).expanduser()
    fp.parent.mkdir(parents=True, exist_ok=True)
    with open(fp, 'a') as f:
        f.write(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"Prompt:\n{prompt}\n\n")
        if response: f.write(f"Response:\n{response}\n\n")
        f.write("---\n")
    print(f"Saved to {fp}", file=sys.stderr)

if __name__ == '__main__': main()
