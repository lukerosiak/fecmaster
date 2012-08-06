import logging
import logging.handlers
import os.path

LOGGING_EMAIL = {'recipients':''}

def set_up_logger(importer_name, log_path, email_subject, email_recipients=LOGGING_EMAIL['recipients']):
    # create logger
    log = logging.getLogger(importer_name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    
    # create console handler and set level to debug
    ch = logging.FileHandler(os.path.join(log_path, importer_name + '.log'))
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    return log

