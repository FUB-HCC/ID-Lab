import os
import jsonloader


slugs = {
    'content_job.json': 'slug_de',
    'content_kooperation.json': 'slug_de',
    'content_nachwuchsfoerderung.json': 'slug_de',
    'content_podcast.json': 'slug_de',
    'content_post.json': 'slug_de',
    'content_pressemitteilung.json': 'slug_de',
    'content_projekt.json': 'slug_de',
    'content_publikation.json': 'slug_de',
    'content_ausstellung.json': 'slug_de',
    'content_category.json': 'slug',
    'content_event.json': 'slug_de',
    'content_mitglied.json': 'slug_de',
    'content_newsletter.json': 'slug_de',
    'content_pagecategoryrelationship.json': 'slug_de',
    'content_pagepagerelationship.json': 'slug_de',
    'taggit_tag.json': 'slug',
    'wagtaildocs_document.json': 'file',
    'wagtailembeds_embed.json': 'url',
    'wagtailimages_image.json': 'id',
    'wagtailimages_rendition.json': 'id'
}



def readp2pmapping(filename, files, idmapping, inputpathjson):
    f = jsonloader.loadjson(inputpathjson + filename.replace("public.", ""))
    print("Loading mapping file " + filename + " with nr of entries: ", len(f) )
    neededMappings = set([])
    counter = 0
    for a in f:
        page1id = a["page1_id"]
        page2id = a["page2_id"]
        #print("Looking for " +  page1id + " to " + page2id + " mapping")
        notFound = True
        if page1id in idmapping:
            p1filename = idmapping[page1id]["filename"]
            p1file = files[p1filename]
            for entry1 in p1file:
                if entry1["page_ptr_id"] == page1id:
                    if page2id in idmapping:
                        p2filename = idmapping[page2id]["filename"]
                        p2file = files[p2filename]
                        for entry2 in p2file:
                            if entry2["page_ptr_id"] == page2id:
                                #p1filename = p1filename.replace(".","_")
                                #p2filename = p2filename.replace(".", "_")
                                if slugs[p1filename] in entry1 and slugs[filename] in entry2:
                                    page1Slug = entry1[slugs[p1filename]]
                                    page2Slug = entry2[slugs[filename]]

                                    if page1Slug != None and page2Slug != None:
                                        if not os.path.splitext(p1filename)[0] + "|||" + os.path.splitext(p2filename)[0] in entry1:
                                            entry1[os.path.splitext(p1filename)[0] + "|||" + os.path.splitext(p2filename)[0]] = []
                                        entry1[os.path.splitext(p1filename)[0] + "|||" + os.path.splitext(p2filename)[0]].append(page2Slug)
                                        neededMappings.add(os.path.splitext(p1filename)[0] + "|||" + os.path.splitext(p2filename)[0])
                                        # print(entry1)
                                        if not os.path.splitext(p2filename)[0] + "|||" + os.path.splitext(p1filename)[0] in entry2:
                                            entry2[os.path.splitext(p2filename)[0] + "|||" + os.path.splitext(p1filename)[0]] = []
                                        entry2[os.path.splitext(p2filename)[0] + "|||" + os.path.splitext(p1filename)[0]].append(page1Slug)
                                        neededMappings.add(os.path.splitext(p2filename)[0] + "|||" + os.path.splitext(p1filename)[0])
                                        # print(entry2)
                                    counter = counter + 1
                                    notFound = False
                                    break
                                else:
                                    print("Missing property " + slugs[filename])
                    break

        if notFound:
            print ("Should have found something.")
    print("Finished. Found nr of mappings:", counter)
    print("Will need mappings for:")
    for m in neededMappings:
        print(m)

def readp2cmapping(filename, files, idmapping, inputpathjson, categories):
    f = jsonloader.loadjson(inputpathjson + filename)
    print("Loading mapping file " + filename + " with nr of entries: ", len(f) )
    neededMappings = set([])
    counter = 0
    for a in f:
        pageid = a["page_id"]
        categoryId = a["category_id"]
        #print("Looking for " +  page1id + " to " + page2id + " mapping")
        notFound = True
        if pageid in idmapping:
            pagefilename = idmapping[pageid]["filename"]
            pagefile = files[pagefilename]
            for entry in pagefile:
                if entry["page_ptr_id"] == pageid:
                    if categoryId in categories:
                        cat = categories[categoryId]
                        #pageFileName = pagefilename.replace(".", "_")
                        toFileNameNoEnding = os.path.splitext(pagefilename)[0]
                        catName = "content_category|||%s" % toFileNameNoEnding
                        if not catName in cat:
                           cat[catName] = []

                        if slugs[pagefilename] in entry and not entry[slugs[pagefilename]] == None :
                            cat[catName].append(entry[slugs[pagefilename]])
                            neededMappings.add("content_category|||" + toFileNameNoEnding)
                            # print(entry1)
                            if not "%s|||content_category" % toFileNameNoEnding in entry:
                                entry["%s|||content_category" % toFileNameNoEnding] = []
                            entry["%s|||content_category" % toFileNameNoEnding].append(cat["slug"])
                            neededMappings.add(os.path.splitext(pagefilename)[0] + "|||content_category")
                            # print(entry2)
                            counter = counter + 1
                        notFound = False
                        break
                    break

        if notFound:
            print ("Should have found something.")
    print("Finished. Found nr of mappings:", counter)
    print("Will need category mappings for:")
    for m in neededMappings:
        print(m)