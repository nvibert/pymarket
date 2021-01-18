# pymarket
A short Python script to interact with the VMware Marketplace


I have built two main commands. First, the 'search-product'. Just put the name of the product you're looking for as an argument (here, I am searching for "Kong").


    $ python3 pymarket.py search-product Kong
    +------------------------+--------------------------------------+---------------+----------------+
    |      Product Name      |                  ID                  | Solution Type | Latest version |
    +------------------------+--------------------------------------+---------------+----------------+
    | Kong Virtual Appliance | b93a9a91-a05f-4262-a96e-ef21c8c6d387 |      OVA      |  2.1.0_8_r06   |
    |  Kong Enterprise 2020  | 0a2f6f6e-8cef-400e-a19e-15454a531d2a |   CONTAINER   |      1.5       |
    |    Kong Helm Chart     | 619dd92f-9732-4e09-b226-30c97748ec36 |   CONTAINER   |     2.1.3      |
    +------------------------+--------------------------------------+---------------+----------------+

The search returns the solution type (my focus is on OVA at the moment so the tool just works for this format at the moment) and the product ID. Once you know the product you want to register, it's easy enough, just use the subscribe command. Use the Product ID and the version as arguments. 

    $ python3 pymarket.py subscribe b93a9a91-a05f-4262-a96e-ef21c8c6d387 2.1.0_8_r06
    Products Deployments Request Accepted: the product image has been added to the Content Library Kong Virtual Appliance---2.1.0_8_r06.
