from command import Command, UsageError

class ContainerCommand(Command):

    name = 'container'

    def short_desc(self):

        return "operate with objectstore containers"

        
    def add_options(self, parser):
        
        Command.add_options(self, parser)
        parser.add_argument("--container", type=str, help="container name")
    

    def process_options(self, args):
        
        Command.process_options(self, args)

        if args.container:
            self.container = args.container
        else:
            raise UsageError('Missed --container parameter')


    def run(self):
    
        pass

