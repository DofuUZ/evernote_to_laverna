import uuid
import os
import datetime
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import OrderedDict


def load_evernote_enex(evernote_enex):
    ''' Takes evernote file and returns a list of
    dictionary notes'''
    tree = ET.parse(evernote_enex)
    root = tree.getroot()
    nlist = []
    for note in root:
        notedict = {}
        notedict['title'] = note[0].text
        notedict['content'] = note[1].text
        notedict['created'] = note[2].text
        notedict['updated'] = note[3].text
        nlist.append(notedict)
    return nlist


def evernote_date_to_millisecond_epoch(evernote_date):
    '''Take evernotes goddamn format and turn it into
    even more insane milliseconds since epoch'''
    time = datetime.datetime.strptime(evernote_date, '%Y%m%dT%H%M%SZ')
    epoch = time.strftime('%s')
    msepoch = int(epoch) * 1000
    return msepoch


def notedict_to_laverna_note(evernote_note_dict):
    title = evernote_note_dict['title']
    created = evernote_note_dict['created']
    updated = evernote_note_dict['updated']
    content = evernote_note_dict['content']
    note_uuid = str(uuid.uuid1())

    note_content = content.encode('utf-8')
    empty = []
    note_json_tuple = [
        ("id", note_uuid),
        ("type", "notes"),
        ("title", title),
        ("taskAll", 0),
        ("taskCompleted", 0),
        ("created", evernote_date_to_millisecond_epoch(created)),
        ("updated", evernote_date_to_millisecond_epoch(updated)),
        ("notebookId", "0"),
        ("tags", empty),
        ("isFavorite", 0),
        ("trash", 0),
        ("files", empty),
        ("tasks", empty)]
    note_json = OrderedDict(note_json_tuple)
    print note_json
    return note_uuid, note_json, note_content


def write_laverna_note_files(note_uuid, note_json, note_content, directory='scratch/notes-db/notes'):
    note_directory = os.path.join(base, directory)
    if not os.path.exists(note_directory):
        os.mkdir(note_directory)

    json_file_name = os.path.join(note_directory, note_uuid + '.json')
    with open(json_file_name, 'w') as json_file:
        json_file.write(json.dumps(note_json))
    content_file_name = os.path.join(note_directory, note_uuid + '.md')
    with open(content_file_name, 'w') as content_file:
        content_file.write(note_content)


def write_other_files(directory='scratch/notes-db'):
    scratch = os.path.join(base, directory)
    if not os.path.exists(scratch):
        os.mkdir(scratch)

    empty = []
    notebook_file = os.path.join(base, directory, 'notebooks.json')
    notebook_file = open(notebook_file, 'w')
    notebook_file.write(json.dumps(empty))

    tag_file = os.path.join(base, directory, 'tags.json')
    tag_file = open(tag_file, 'w')
    tag_file.write(json.dumps(empty))

    config_file = 'configs.json'
    #config_file = open(config_file, 'w')
    #config_file.write((json.dumps(empty)))

    if not os.path.exists('notes'):
        os.mkdir('notes')

base = os.getcwd()
# evernote_enex_file = 'evernote.enex'
#
# nlist = load_evernote_enex(evernote_enex_file)
# for i in nlist:
#     note_json, note_content, note_uuid = notedict_to_laverna_note(i)
#     write_laverna_note_files(note_json, note_content, note_uuid)
# write_other_files()

def create_zip(directory):
    with zipfile.ZipFile('zipfile.zip', 'w') as zip:
        for root, dir, file in os.walk(directory):
            print root
            if os.path.isfile(file):
                print os.path.join(base, file)
                zip.write(os.path.join(base, file))
        zip.close()
create_zip(base)
