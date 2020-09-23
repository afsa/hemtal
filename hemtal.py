#!/usr/bin/env python3
import argparse
import logging
import os
import smtplib
from email.message import EmailMessage
from getpass import getpass
from pathlib import Path
from shutil import copyfile


def parse_arguments():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='move solutions or send email to students.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='run in verbose mode')
    subparsers = parser.add_subparsers()

    # Parse move solutions command
    parse_move_sol = subparsers.add_parser('move', help='move solutions from separate folders to one single folder')
    parse_move_sol.add_argument('input', metavar='INPUT', type=str, help='folder that contains the solutions')
    parse_move_sol.add_argument('output', metavar='OUTPUT', type=str, help='output folder for the moved solutions')
    parse_move_sol.add_argument('--overwrite', action='store_true', default=False,
                                help='overwrite solution if it already exists')
    parse_move_sol.set_defaults(func=move_solutions)

    # Parse email solutions
    parse_email = subparsers.add_parser('email', help='send email to students')
    parse_email.add_argument('input', metavar='INPUT', type=str, help='path to folder that contains the solutions')
    parse_email.set_defaults(func=send_email)

    args = parser.parse_args()

    # Enable logging
    logger = logging.getLogger('hemtal')
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    console_stream = logging.StreamHandler()
    console_stream.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console_stream)

    args.func(args, logger)


def move_solutions(args, logger):
    inp = Path(args.input)
    out = Path(args.output)

    # Make sure that the input path is a dir
    if not inp.is_dir():
        logger.fatal('ERROR: INPUT needs to be a directory.')
        return

    # Make sure that the output path is a dir
    if not out.is_dir():
        logger.fatal('ERROR: OUTPUT needs to be a directory.')
        return

    # Get all subdirs
    dirs = [o for o in os.listdir(str(inp)) if os.path.isdir(os.path.join(str(inp), o))]

    num_sol = 0

    for solution in dirs:
        solution_file = os.path.join(str(inp), solution, '0.pdf')
        output_file = os.path.join(str(out), '{}.pdf'.format(solution))

        # Inform user that solution does not exist
        if not os.path.exists(solution_file):
            logger.warning('WARNING: {} does not exist OR THE STUDENT SENT A .png FILE :)'.format(solution_file))
            continue

        # Inform user that solution is already copied
        if os.path.exists(output_file) and not args.overwrite:
            logger.info('INFO: {} already exists, skipping'.format(solution))
            continue

        copyfile(solution_file, output_file)
        num_sol += 1

    logger.info('Successfully moved {} solutions to {}'.format(num_sol, str(out)))


def send_email(args, logger):
    inp = Path(args.input)

    # Make sure that the input path is a dir
    if not inp.is_dir():
        logger.fatal('ERROR: INPUT needs to be a directory.')
        return

    subject = input('Subject: ')
    content = get_contents()
    from_email = input('Your email: ')

    try:
        from_email_array = from_email.split('@')
        user = from_email_array[0]
        domain = from_email_array[1]
    except ValueError:
        logger.fatal('ERROR: Invalid email address.')
        return

    password = getpass('Password: ')

    solutions = sorted([o for o in os.listdir(str(inp)) if not os.path.isdir(os.path.join(str(inp), o))
                        and o.endswith('.pdf')])

    num_email = 0

    with smtplib.SMTP_SSL('smtp.{}'.format(domain)) as s:
        s.login(user, password)

        for i, solution in enumerate(solutions):
            # Get email from files
            to_email = (solution.split('-')[-1])[:-4]

            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            msg.set_content(content)

            # Add attachment
            with open(os.path.join(str(inp), solution), 'rb') as fp:
                data = fp.read()
                msg.add_attachment(data, filename=solution, maintype='application', subtype='pdf')

            # Send email
            try:
                s.send_message(msg)
                logger.info('{}: Sent {}'.format(i, solution))
                num_email += 1
            except smtplib.SMTPSenderRefused:
                logger.fatal('ERROR: Could not send {}'.format(solution))
                pass

    logger.info('Successfully sent {} emails.'.format(num_email))


def get_contents():
    print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    return '\n'.join(contents)


if __name__ == '__main__':
    parse_arguments()
