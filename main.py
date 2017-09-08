"""The main entry point."""

import logging
import os
import os.path
from default_argparse import parser
from leatherman import app
from leatherman.ui.main_frame import MainFrame
from leatherman.config import config

if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level, stream=args.log_file, format=args.log_format
    )
    app.frame = MainFrame(None, title=app.name)
    app.frame.Show(True)
    app.frame.Maximize()
    config.load()
    app.app.MainLoop()
    if not os.path.isdir(app.data_dir):
        os.makedirs(app.data_dir)
    config.write(indent=4)
