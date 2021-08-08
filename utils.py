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


def get_project_dir(name):
    if not os.path.isdir(OUTPUT):
        os.mkdir(OUTPUT)

    dir_name = os.path.join(OUTPUT, name)
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
        return dir_name
    else:
        i = 1
        while True:
            temp_name = dir_name + f'_{i}'
            if not os.path.isdir(temp_name):
                os.mkdir(temp_name)
                return temp_name
            i += 1
