import pandas as pd
import streamlit as st
import functions
import datetime
import time


def show():



    aVendorType = ["Entertainment", "Caterers", "Venues"]
    vendor_type = st.sidebar.selectbox("Which vendor type applies to you?", aVendorType)

    if (vendor_type == "Entertainment"):
        st.write("# Entertainment Portal")
        show_entertainment_view()

    if (vendor_type == "Caterers"):
        st.write("# Caterer Portal")
        show_caterer_view()

    if (vendor_type == "Venues"):
        st.write("# Venue Portal")
        show_venue_view()


def show_caterer_view():
    vendor_type = "Caterers"
    resource_type = "Caterer"

    q_vendors = "SELECT resourceType, typeid, name FROM resources_" + vendor_type + ";"
    df_vendors = functions.query_db(q_vendors)
    a_vendor_names = df_vendors['name'].tolist()
    a_vendor_ids = df_vendors['typeid'].tolist()
    vendor_name = st.sidebar.selectbox("Who are you?", a_vendor_names)

    type_id = a_vendor_ids[a_vendor_names.index(vendor_name)]

    st.write('### My menus')
    q_menus_accom = "SELECT m.name, m.description, a.accommodation FROM menus_offered m LEFT JOIN menus_accommodate a "\
                    + "ON m.menuid = a.menuid WHERE m.caterer_name = \'" + vendor_name.replace("'", "''") + "\';"
    df_menus_accom = functions.query_db(q_menus_accom)

    st.dataframe(df_menus_accom.rename(
        columns={'name': 'Menu', 'description': 'Description', 'accommodation': 'Dietary Accommodation'}))

    show_requirements_section(resource_type, type_id)


def show_entertainment_view():
    vendor_type = "Entertainment"
    resource_type = vendor_type

    st.write('### My gigs')
    st.write('Coming soon')

    q_vendors = "SELECT resourceType, typeid, name, genre FROM resources_" + vendor_type + ";"
    df_vendors = functions.query_db(q_vendors)
    a_vendor_names = df_vendors['name'].tolist()
    a_vendor_ids = df_vendors['typeid'].tolist()
    vendor_name = st.sidebar.selectbox("Who are you?", a_vendor_names)
    type_id = a_vendor_ids[a_vendor_names.index(vendor_name)]

    show_requirements_section(resource_type, type_id)


def show_venue_view():
    vendor_type = "Venues"
    resource_type = "Venue"

    st.write('### My reservations')
    st.write('Coming soon')

    q_vendors = "SELECT resourceType, typeid, name, address FROM resources_" + vendor_type + ";"
    df_vendors = functions.query_db(q_vendors)
    a_vendor_names = df_vendors['name'].tolist()
    a_vendor_ids = df_vendors['typeid'].tolist()
    vendor_name = st.sidebar.selectbox("Who are you?", a_vendor_names)

    type_id = a_vendor_ids[a_vendor_names.index(vendor_name)]

    show_requirements_section(resource_type, type_id)


def show_requirements_section(resource_type, type_id):

    st.write('### My requirements')

    q_required = "SELECT e.name, r.numRequired, r.specification FROM resources_require r," \
                 + " resources_equipment e WHERE r.r1resourceType = \'" + resource_type + "\' AND r.r1typeID = " \
                 + str(type_id) + " AND r.r2typeID = e.typeID;"

    # use a non-cached query function for this - we want to see our updates.
    df_required = pd.DataFrame(columns=['name', 'numrequired', 'specification'])
    df_required = df_required.append(functions.query_db_no_cache(q_required))

    if st.button("Refresh List"):
        st.dataframe(df_required.rename(columns={'name': 'Equipment', 'numrequired': 'Quantity', 'specification': 'Description'}))
    else:
        st.dataframe(df_required.rename(columns={'name': 'Equipment', 'numrequired': 'Quantity', 'specification': 'Description'}))

    st.write('#### Add requirement')

    # Let the user select from all types of equipment
    q_equipment_type = "SELECT DISTINCT equipmentType FROM resources_equipment;"
    df_equipment_types = functions.query_db(q_equipment_type)
    a_equipment_types = df_equipment_types['equipmenttype'].tolist()
    equipment_type = st.selectbox("Select equipment type", a_equipment_types)

    # let the user select from all equipment of that type
    q_equipment = "SELECT name, vendor, typeID FROM resources_equipment " + \
                  "WHERE equipmenttype = \'" + equipment_type + "\';"
    df_equipment = functions.query_db(q_equipment)
    df_equipment['equipment_vendor'] = (df_equipment['name'] + ' (' + df_equipment['vendor'] + ')')

    # get the names, typeIDs, and vendor of all equipment
    a_equipment = df_equipment['name'].tolist()
    a_equipment_vendor = df_equipment['equipment_vendor'].tolist()
    a_equipment_id = df_equipment['typeid'].tolist()

    # let the user select a piece of equipment
    equipment_vendor = st.selectbox("", a_equipment_vendor)
    equipment = a_equipment[a_equipment_vendor.index(equipment_vendor)]
    equipment_id = a_equipment_id[a_equipment_vendor.index(equipment_vendor)]

    # let the user specify a quantity and a descriptioon
    quantity = st.number_input("Quantity", value=0, step=1)
    specification = st.text_input('Description', max_chars=120)

    if st.button('Add'):

        # check to see that the user hasn't asked for more equipment than we can source
        q_max_quantity = "SELECT quantity FROM resources_equipment " + \
                         "WHERE equipmenttype = \'" + equipment_type + "\' AND name = \'" + equipment + "\';"
        df_max_quantity = functions.query_db(q_max_quantity)
        max_quantity = df_max_quantity['quantity'][0]

        if quantity > max_quantity:
            st.write("You require more of this item than we have available. Sorry!")
            st.write("Stock: " + str(max_quantity))

        else:

            # insert a new resources_require entry!
            q_require = "INSERT INTO " \
                        "resources_require(r1resourceType,r1typeID,r2resourceType,r2typeID,numRequired,specification) " \
                        "VALUES ('{0}', {1},'Equipment', {2}, {3}, '{4}');" \
                .format(resource_type, type_id, equipment_id, quantity, specification.replace("'", "''"))

            # append a row to our DF since we can't count on an instantaneous update
            data = [[equipment, quantity, specification]]
            row = pd.DataFrame(data, columns=['name', 'numrequired', 'specification'])

            df_required = df_required.append(row)

            # use a non-cached execution function to execute our insert statment
            functions.execute_db(q_require)

    return
