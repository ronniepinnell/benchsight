# Quick Fix for ETL Error

## Copy and paste this command:

```bash
cd "/Users/ronniepinnell/Documents/Documents - Ronnie's MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight" && python3 -c "
import re
file_path = 'src/core/base_etl.py'
with open(file_path, 'r') as f:
    content = f.read()
if 'existing_pull_cols' in content:
    print('Already fixed!')
else:
    # Create backup
    with open(file_path + '.backup', 'w') as f:
        f.write(content)
    # Find and replace
    pattern = r'(sp\s*=\s*sp\.merge\s*\(\s*shifts_for_merge\[)all_pull_cols(\])'
    def replacer(m):
        indent = ' ' * (len(m.group(0)) - len(m.group(0).lstrip()))
        return f'{indent}# Filter all_pull_cols to only existing columns\n{indent}existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]\n{indent}sp = sp.merge(shifts_for_merge[existing_pull_cols'
    new_content = re.sub(pattern, replacer, content)
    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print('Fix applied!')
    else:
        print('Pattern not found - applying manual fix...')
        # Manual approach: find the line and fix it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'shifts_for_merge[all_pull_cols]' in line and 'merge' in line.lower():
                indent = ' ' * (len(line) - len(line.lstrip()))
                lines[i] = f'{indent}# Filter all_pull_cols to only existing columns\n{indent}existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]\n' + line.replace('all_pull_cols', 'existing_pull_cols')
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                print('Fix applied!')
                break
        else:
            print('Could not find the line to fix')
"
```

## Or manually edit:

1. Open: `src/core/base_etl.py`
2. Go to line 5099
3. Find: `sp = sp.merge(shifts_for_merge[all_pull_cols], left_on='shift_id', right_index=True, how='left')`
4. Replace with:
   ```python
   # Filter all_pull_cols to only existing columns
   existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]
   sp = sp.merge(shifts_for_merge[existing_pull_cols], left_on='shift_id', right_index=True, how='left')
   ```
