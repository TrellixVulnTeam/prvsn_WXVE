import getpass
import logging
import pty
import os

from prvsnlib.utils.file import mkdir_p


class Ssh:
    def __init__(self, remote='localhost', user=getpass.getuser(), password=None):
        self.hostname = remote
        self.username = user
        self._password = password

    def __str__(self):
        return '<SSH ' + self.username + '@' + self.hostname + '>'

    @property
    def remote(self):
        return self.hostname + '@' + self.username

    def command(self, commands, log_output=logging.debug, sudo=False):
        commands_to_run = [
            '/usr/bin/ssh',
            self.username + '@' + self.hostname,
        ]

        if sudo:
            commands_to_run += ['sudo', '-p', 'sudo password: ']

        commands_to_run += commands

        return self.run(
            commands_to_run,
            log_output=log_output
        )

    def copyTo(self, src, dest, log_output=logging.debug):
        out1 = ''
        err1 = ''
        if os.path.dirname(dest):
            out1, err1 = self.run([
                    '/usr/bin/ssh',
                self.username + '@' + self.hostname,
                    'mkdir -p ' + os.path.dirname(dest),
                ],
                log_output=log_output
            )
        if err1:
            return out1, err1
        out2, err2 = self.run([
                '/usr/bin/scp',
                src,
            self.username + '@' + self.hostname + ':' + dest,
            ],
            log_output=log_output
        )
        return out1 + '\n' + out1, err1 + err2

    def copyFrom(self, src, dest, log_output=logging.debug):
        mkdir_p(os.path.dirname(dest))
        return self.run([
                '/usr/bin/scp',
            self.username + '@' + self.hostname + ':' + src,
                dest,
            ],
            log_output=log_output,
        )

    def run(self, commands, log_output=logging.debug):
        logging.debug('Running "' + ' '.join(commands) + '"')

        pid, child_fd = pty.fork()

        def is_child_pid(pid):
            return not pid

        if is_child_pid(pid):
            os.execv(commands[0], commands)

        password = ''
        password_attempted = False

        output = []
        while True:

            try:
                r = os.read(child_fd, 1024).strip()
                wpid, wret, wres = os.wait4(pid, os.WNOHANG)
            except Exception as e:
                break
            lower = r.lower()

            if b'are you sure you want to continue connecting' in lower:
                logging.debug('Adding host to known hosts')
                os.write(child_fd, b'yes\n')

            elif b'password:' in lower:
                if self._password:
                    password = self._password
                else:
                    password = getpass.getpass(prompt='Password for user "' + self.username + '": ')
                    password_attempted = True

                logging.debug('Sending SSH password')
                os.write(child_fd, password.encode('utf-8') + b'\n')

            elif r:
                output.append(r.decode('utf-8')+'\n')

            if wret:
                err = '\n'.join(output)
                logging.error(err)
                return '', err

            if password_attempted and password and lower and b'uthentication fail' not in lower:
                logging.debug('SSH authenticated')
                self._password = password
                password_attempted = False

        out = ''.join(output)
        log_output(out)
        return out, ''