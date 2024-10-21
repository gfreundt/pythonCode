# import members, updates, scrapers


def side(MONITOR):
    # function used for testing
    print("************* RUNNING SIDE *************")
    MEMBERS = members.Members(LOG, MONITOR)
    members.process_unsub.process_unsub(MEMBERS, LOG)
    MEMBERS.create_30day_list()
    UPD = updates.Update(LOG, MEMBERS, MONITOR)
    UPD.all_updates = {"soats": [(1, "DNI", "08257907")]}
    # UPD.get_records_to_process()
    print(UPD.all_updates)
    UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
    return

    MONITOR.add_item("SOATS...", type=1)
    UPD.gather_soat(scraper=scrapers.Soat(), table="soats", date_sep="-")
    return

    MEMBERS.create_30day_list()
    MAINT = maintenance.Maintenance(LOG, MEMBERS)
    MAINT.soat_images()
    return
