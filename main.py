"""The main entry point."""

import logging
import os
import os.path
from default_argparse import parser
from mmp import app
from mmp.ui.main_frame import MainFrame
from mmp.ui.lyrics_frame import LyricsFrame
from mmp.config import config
from mmp.db import session, Hotkey, Section

parser.set_defaults(
    log_file=os.path.join(
        app.data_dir, '%s.log' % app.name
    ),
    log_format='%(name)s.%(levelname)s: %(message)s'
)

parser.add_argument(
    '-c',
    '--clear-db',
    action='store_true',
    help='Clear the database to restore defaults'
)

if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level, stream=args.log_file, format=args.log_format
    )
    if args.clear_db:
        logging.info('Clearing the database.')
        with session() as s:
            for table in (Hotkey, Section):
                q = s.query(table)
                n = q.count()
                logging.info('Clearing table %s.', table.__table__.name)
                q.delete()
                logging.info('Rows affected: %d.', n)
    app.lyrics_frame = LyricsFrame(None)
    app.frame = MainFrame(None, title=app.name)
    app.frame.Show(True)
    app.frame.Maximize()
    app.app.MainLoop()
    if not os.path.isdir(app.data_dir):
        os.makedirs(app.data_dir)
    config.write(indent=4)
