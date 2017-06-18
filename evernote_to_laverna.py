#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import os
import datetime
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import OrderedDict

import html2text


text_maker = html2text.HTML2Text()
text_maker.body_width = 0
text_maker.unicode_snob = True
text_maker.single_line_break = True


def load_evernote_enex(evernote_enex):
    ''' Takes evernote file and returns a list of
    dictionary notes'''
    print(evernote_enex)
    tree = ET.parse(evernote_enex)
    root = tree.getroot()
    nlist = []
    for note in root:
        notedict = {}
        notedict['title'] = note.find('title').text
        notedict['content'] = note.find('content').text
        notedict['created'] = note.find('created').text
        try:
            notedict['updated'] = note.find('updated').text
        except AttributeError:
            pass

        nlist.append(notedict)
    return nlist


def evernote_date_to_millisecond_epoch(evernote_date):
    '''Take evernotes goddamn format and turn it into
    even more insane milliseconds since epoch'''
    time = datetime.datetime.strptime(evernote_date, '%Y%m%dT%H%M%SZ')
    epoch = time.timestamp()
    msepoch = int(epoch * 1000)
    return msepoch


def notedict_to_laverna_note(evernote_note_dict):
    title = evernote_note_dict['title']
    created = evernote_note_dict['created']
    content = evernote_note_dict['content']
    note_uuid = str(uuid.uuid1())

    note_content = text_maker.handle(content).replace('\n  \n', '\n\xA0')

    note_json_tuple = [
        ("id", note_uuid),
        ("type", "notes"),
        ("title", title),
        ("taskAll", 0),
        ("taskCompleted", 0),
        ("created", evernote_date_to_millisecond_epoch(created)),
        ("notebookId", "0"),
        ("tags", []),
        ("isFavorite", 0),
        ("trash", 0),
        ("files", []),
        ("tasks", [])]
    try:
        updated = evernote_note_dict['updated']
        note_json_tuple.append(
            ("updated", evernote_date_to_millisecond_epoch(updated))
        )
    except KeyError:
        pass

    note_json = OrderedDict(note_json_tuple)
    print(note_json)
    return note_uuid, note_json, note_content


def write_laverna_note_files(note_uuid, note_json, note_content, directory='laverna-backup/notes-db/notes'):
    os.makedirs(directory, exist_ok=True)

    json_file_name = os.path.join(directory, note_uuid + '.json')
    with open(json_file_name, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(note_json))
    content_file_name = os.path.join(directory, note_uuid + '.md')
    with open(content_file_name, 'w', encoding='utf-8') as content_file:
        content_file.write(note_content)


def create_skeleton(directory='laverna-backup'):
    if not os.path.exists(directory):
        os.mkdir(directory)

    notesdb_directory = os.path.join(directory, 'notes-db')
    if not os.path.exists(notesdb_directory):
        os.mkdir(notesdb_directory)

    notes_directory = os.path.join(notesdb_directory, 'notes')
    if not os.path.exists(notes_directory):
        os.mkdir(notes_directory)

    notebook_path = os.path.join(directory, 'notes-db/notebooks.json')
    with open(notebook_path, 'w', encoding='utf-8') as notebook_file:
        notebook_file.write(json.dumps([]))

    tag_path = os.path.join(directory, 'notes-db/tags.json')
    with open(tag_path, 'w', encoding='utf-8') as tag_file:
        tag_file.write(json.dumps([]))


def create_zip(directory, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file = os.path.join(root, file)
                print(file)
                zipf.write(file)


if __name__ == '__main__':
    evernote_enex_file = sys.argv[1]
    create_skeleton()
    nlist = load_evernote_enex(evernote_enex_file)
    for i in nlist:
        note_json, note_content, note_uuid = notedict_to_laverna_note(i)
        write_laverna_note_files(note_json, note_content, note_uuid)
    create_zip('laverna-backup', 'laverna.zip')
