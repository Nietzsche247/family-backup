import sys, io, os

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['OMP_NUM_THREADS'] = '4'

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from mempalace.cli import main

SOURCE_DIR = r"C:\Users\aaron\mempalace-staging\shared"
WING = 'shared'

sys.argv = ['mempalace', 'mine', SOURCE_DIR, '--wing', WING]

try:
    main()
except SystemExit:
    pass
