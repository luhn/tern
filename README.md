Tern
====

**Tern** is a simple way to version control your database.  It integrates with git (Support for more SCMs upcoming), and you can use it to distribute and manage schema changes across git branches, team members, and servers.

Quickstart
----------

First, install tern:

    $ pip install tern
    
Now, in the root of your repository, run the `setup` command.

    $ tern setup models/
    DBMS (Choose `postgres` or `sqlite`):  postgres
    Host [localhost]:  
    DB name:  tern
    Username:  postgres
    Password:  awesome
    Running setup...  Done.
    
This will set up tern in your repository and store all the schema changes in the `models/` directory.  Now we can run the `update` command to get the most up-to-date version of the database.

    $ tern update
    Checking for downgrades...  0
    Checking for upgrades...  0
    
Of course, that's not unexpected.  We haven't done anything yet!  Let's add a schema change.  You'll notice a file in the repository root called `setup.tern.sql`.  Open it up and add some SQL to it:

    CREATE TABLE person (
      id SERIAL PRIMARY KEY,
      forename TEXT NOT NULL,
      surname TEXT NOT NULL
    );
    
Now that we've told tern how to install this change, we need to tell it how to remove the change.  Open up and edit `teardown.tern.sql`:

    DROP TABLE person;
    
Let's make sure we did everything right:

    $ tern test
    Applying change...  Done.
    Reversing change...  Done.
    Everything looks good!
    
Now let's finally commit our SQL changes.

    $ tern apply
    $ tern update
    Checking for downgrades...  0
    Checking for upgrades...  1
    Applying upgrades...  1/1
    $ git commit
    
      
