import musicbrainzngs

# 'Backsamples' means when the artist gets sampled by someone else. Off by default.
DISPLAY_BACKSAMPLES = False


def select_artist():
    name = input("Select artist: ")
    result = musicbrainzngs.search_artists(artist=name)
    counter = 0
    for artist in result['artist-list']:
        counter = counter + 1
        print("Result #" + str(counter) + ": " + u"{id}: {name}".format(id=artist['id'], name=artist["name"]))
    if counter == 0:
        # If no results found.
        print("No results found for search '" + name + ".'")
        return select_artist()
    elif counter == 1:
        # If there was only one result, print
        return result['artist-list'][0]
    else:
        def get_index(max_value: int):
            index_of_choice = int(input("Which number result was it?: "))
            if index_of_choice > max_value or index_of_choice < 1:
                print("Out of bounds. Please enter a number between 1 and " + str(max_value) + ".")
                get_index(max_value)
            return index_of_choice

        num = get_index(counter)
        return result['artist-list'][num - 1]


def search_for_samples(recording_batch):
    for my_recording in recording_batch:
        try:
            rec_rels = my_recording['recording-relation-list']
        except KeyError:
            # Guess there were no recording-relationships.
            continue

        if rec_rels is not None:
            for recording_relationship in rec_rels:
                if recording_relationship['type'] == 'samples material':
                    # If there are samples...
                    sampled_audio = recording_relationship['recording']
                    sampled_artist = musicbrainzngs.browse_artists(recording=sampled_audio['id'])['artist-list'][0]
                    direction = recording_relationship['direction']
                    if direction == 'forward':
                        # Artist is sampling someone else.
                        print(
                            my_recording['title'] + " samples " + sampled_audio['title'] + " by " + sampled_artist[
                                'name'])
                    elif DISPLAY_BACKSAMPLES:  # direction == 'backward'
                        # Artist is *being* sampled.
                        print(my_recording['title'] + " is sampled by " + sampled_audio['title'] + " by " +
                              sampled_artist['name'])


def main():
    musicbrainzngs.set_useragent("test app for finding all samples in artist's discography",
                                 "0.1", "calebcopeland1@gmail.com")
    musicbrainzngs.set_rate_limit(limit_or_interval=1.0, new_requests=1)

    artist_id = select_artist()['id']
    batch_index = 0
    found_anything = True
    while found_anything:
        res = musicbrainzngs.browse_recordings(
            artist=artist_id, offset=batch_index * 25,
            includes=['recording-rels'])['recording-list']
        found_anything = False
        my_recordings = []
        for recording in res:
            my_recordings.append(recording)
            found_anything = True
        batch_index = batch_index + 1
        print("Scanning batch #" + str(batch_index) + " for samples...")
        search_for_samples(my_recordings)


main()
