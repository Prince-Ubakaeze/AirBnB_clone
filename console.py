#!/usr/bin/python3
"""Command interpreter for the AirBnB clone."""

import cmd
import shlex

from models import storage
from models.engine.file_storage import CLASSES


class HBNBCommand(cmd.Cmd):
    """Create, inspect, update, and delete stored model instances."""

    prompt = "(hbnb) "
    classes = CLASSES

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """Exit the program at the end of input."""
        return True

    def emptyline(self):
        """Do nothing when the user enters an empty line."""
        pass

    def _arguments(self, arg):
        """Split arguments while preserving quoted strings."""
        try:
            return shlex.split(arg)
        except ValueError:
            print("** invalid syntax **", file=self.stdout)
            return None

    def _class_name(self, args):
        """Validate the class argument and return its name."""
        if args is None:
            return None
        if not args:
            print("** class name missing **", file=self.stdout)
            return None
        if args[0] not in self.classes:
            print("** class doesn't exist **", file=self.stdout)
            return None
        return args[0]

    def _instance(self, args):
        """Validate a class and ID, then return the stored instance."""
        class_name = self._class_name(args)
        if class_name is None:
            return None
        if len(args) < 2:
            print("** instance id missing **", file=self.stdout)
            return None
        key = "{}.{}".format(class_name, args[1])
        instance = storage.all().get(key)
        if instance is None:
            print("** no instance found **", file=self.stdout)
        return instance

    def do_create(self, arg):
        """Create and save an instance: create BaseModel or create <class>."""
        args = self._arguments(arg)
        class_name = self._class_name(args)
        if class_name is not None:
            instance = self.classes[class_name]()
            instance.save()
            print(instance.id, file=self.stdout)

    def do_show(self, arg):
        """Print an instance: show <class name> <id>."""
        instance = self._instance(self._arguments(arg))
        if instance is not None:
            print(instance, file=self.stdout)

    def do_destroy(self, arg):
        """Delete and save the change: destroy <class name> <id>."""
        args = self._arguments(arg)
        instance = self._instance(args)
        if instance is not None:
            del storage.all()["{}.{}".format(args[0], args[1])]
            storage.save()

    def do_all(self, arg):
        """Print a list of instances: all [class name]."""
        args = self._arguments(arg)
        if args is None:
            return
        if args and self._class_name(args) is None:
            return
        instances = storage.all().values()
        print([str(obj) for obj in instances
               if not args or type(obj).__name__ == args[0]], file=self.stdout)

    def _attribute_value(self, instance, attribute, value):
        """Keep declared types and infer numbers for new attributes."""
        current_value = getattr(type(instance), attribute, None)
        if current_value is None:
            current_value = getattr(instance, attribute, None)
        if current_value is not None:
            value_type = type(current_value)
            if value_type not in (str, int, float):
                raise ValueError("Only simple attributes can be updated")
            return value_type(value)
        for value_type in (int, float):
            try:
                return value_type(value)
            except ValueError:
                continue
        return value

    def do_update(self, arg):
        """Update one attribute: update <class name> <id> <name> <value>."""
        args = self._arguments(arg)
        instance = self._instance(args)
        if instance is None:
            return
        if len(args) < 3:
            print("** attribute name missing **", file=self.stdout)
            return
        if len(args) < 4:
            print("** value missing **", file=self.stdout)
            return
        attribute, value = args[2:4]
        if attribute in ("id", "created_at", "updated_at"):
            return
        if (attribute.startswith("_")
                or callable(getattr(type(instance), attribute, None))
                or callable(getattr(instance, attribute, None))):
            print("** invalid attribute name **", file=self.stdout)
            return
        try:
            value = self._attribute_value(instance, attribute, value)
        except (TypeError, ValueError, OverflowError):
            print("** invalid attribute value **", file=self.stdout)
            return
        setattr(instance, attribute, value)
        instance.save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()
