from nbconvert.writers import FilesWriter


class Writer(FilesWriter):

    def write(self, output, resources, notebook_name=None, **kw):

        # remove the dataframe styles from markdown
        while "<style scoped>" in output:
            start = output.index("<style scoped>")
            end = output.index("</style>\n")+9
            output = output[:start] + output[end:]

        super().write(output, resources, notebook_name, **kw)

