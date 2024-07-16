# Adding a new documentation page

This is a quick guide for adding a new documentation page and running the
documentation locally.

## Prerequisites

Follow the [general setup guide](/general/general_setup.md) to set up `ov`.

## Starting up

The following demonstrates the process of adding a new documentation page.

1. Create a markdown file at a place within the `documentation/` hierarchy that
   makes the most sense for your case. Usually the parent folder for the new
   file would already contain an `index.md` file, make sure that your new file
   is located next to it. If a new directory is required, you will also need to
   create an `index.md` file for it with a table of contents for the folder. See
   other `index.md` files within the `documentation/` directory for examples.

   For instance, adding a new documentation file `dag_testing.md` for describing
   how to test/run the catalog DAGs would likely have you adding the file in
   `documentation/catalog/guides/`.

2. Make an entry with the name of the new document (excluding the `.md` file
   extension) in the closest `index.md`. For our `dag_testing.md` instance, this
   would mean adding `dag_testing` to `documentation/catalog/guides/index.md`.

3. Write the document using [MyST flavored Markdown](https://mystmd.org/guide).

4. Run `ov just lint` to properly format the document.

5. Run `ov just documentation/live` locally (following the quick start guide)
   and navigate to the new page to make sure it looks okay!
