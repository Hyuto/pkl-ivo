import os, logging

OUTPUT = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')


def check_dir(filename):
    """ Check directory and filename """
    if not os.path.isdir(OUTPUT):
        os.mkdir(OUTPUT)

    if os.path.isfile(os.path.join(OUTPUT, filename)):
        logging.warning('Terdapat file lama!')
        user = input('   *  Overwrite? [y/n] ')
        print()
        if user.lower() == 'y':
            return (True, os.path.join(OUTPUT, filename))
        elif user.lower() == 'n':
            return (False, None)
        else:
            raise NotImplementedError('Input error!')
    return (True, os.path.join(OUTPUT, filename))