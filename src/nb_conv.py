from nbconvert.writers import FilesWriter


class Writer(FilesWriter):

    def write(self, output, resources, notebook_name=None, **kw):
        output = output.replace("""}\n\n    .dataframe""", "}\n    .dataframe")
        super().write(output, resources, notebook_name, **kw)

