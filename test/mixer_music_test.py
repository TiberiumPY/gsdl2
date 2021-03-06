import sys
if __name__ == '__main__':
    import os
    pkg_dir = os.path.split(os.path.abspath(__file__))[0]
    parent_dir, pkg_name = os.path.split(pkg_dir)
    is_pygame_pkg = (pkg_name == 'tests' and
                     os.path.split(parent_dir)[1] == 'gsdl2')
    if not is_pygame_pkg:
        sys.path.insert(0, parent_dir)
else:
    is_pygame_pkg = __name__.startswith('gsdl2.tests.')

if is_pygame_pkg:
    from gsdl2.tests.test_utils \
         import test_not_implemented, unittest, example_path
else:
    from test.test_utils \
         import test_not_implemented, unittest, example_path
import gsdl2
from gsdl2.compat import bytes_, filesystem_encode

import os
import io
import time


class MixerMusicModuleTest(unittest.TestCase):
    def test_load(self):
        # __doc__ (as of 2008-07-13) for gsdl2.mixer_music.load:
        
          # gsdl2.mixer.music.load(filename): return None
          # Load a music file for playback

        data_fname = example_path('data')
        gsdl2.mixer.init()

        # The mp3 test file can crash smpeg on some systems.
        ## formats = ['mp3', 'ogg', 'wav']
        formats = ['ogg', 'wav']

        for f in formats:
            path = os.path.join(data_fname, 'house_lo.%s' % f)
            if os.sep == '\\':
                path = path.replace('\\', '\\\\')
            umusfn = path
            if isinstance(umusfn, bytes_):
                umusfn = path.decode('ascii')
            bmusfn = filesystem_encode(umusfn) 
    
            gsdl2.mixer.music.load(umusfn)
            gsdl2.mixer.music.load(bmusfn)

            # Test loading from filelikes objects
            gsdl2.mixer.music.load(open(bmusfn))
            musf = open(bmusfn)
            gsdl2.mixer.music.load(musf)
        gsdl2.mixer.quit()

    def todo_test_queue(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.queue:

          # This will load a music file and queue it. A queued music file will
          # begin as soon as the current music naturally ends. If the current
          # music is ever stopped or changed, the queued song will be lost.
          # 
          # The following example will play music by Bach six times, then play
          # music by Mozart once:
          # 
          #     gsdl2.mixer.music.load('bach.ogg')
          #     gsdl2.mixer.music.play(5)        # Plays six times, not five!
          #     gsdl2.mixer.music.queue('mozart.ogg')

        self.fail() 

    def todo_test_stop(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.stop:

          # Stops the music playback if it is currently playing. 

        self.fail() 

    def todo_test_rewind(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.rewind:

          # Resets playback of the current music to the beginning. 

        self.fail() 

    def todo_test_get_pos(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.get_pos:

          # This gets the number of milliseconds that the music has been playing
          # for. The returned time only represents how long the music has been
          # playing; it does not take into account any starting position
          # offsets.
          # 

        self.fail() 

    def todo_test_fadeout(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.fadeout:

          # This will stop the music playback after it has been faded out over
          # the specified time (measured in milliseconds).
          # 
          # Note, that this function blocks until the music has faded out. 

        self.fail() 

    def todo_test_play(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.play:

          # This will play the loaded music stream. If the music is already
          # playing it will be restarted.
          # 
          # The loops argument controls the number of repeats a music will play.
          # play(5) will cause the music to played once, then repeated five
          # times, for a total of six. If the loops is -1 then the music will
          # repeat indefinitely.
          # 
          # The starting position argument controls where in the music the song
          # starts playing. The starting position is dependent on the format of
          # music playing. MP3 and OGG use the position as time (in seconds).
          # MOD music it is the pattern order number. Passing a startpos will
          # raise a NotImplementedError if it cannot set the start position
          # 

        self.fail() 

    def todo_test_load(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.load:

          # This will load a music file and prepare it for playback. If a music
          # stream is already playing it will be stopped. This does not start
          # the music playing.
          # 
          # Music can only be loaded from filenames, not python file objects
          # like the other gsdl2 loading functions.
          # 

        self.fail() 

    def todo_test_get_volume(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.get_volume:

          # Returns the current volume for the mixer. The value will be between
          # 0.0 and 1.0.
          # 

        self.fail() 

    def test_set_endevent(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.set_endevent:

          # This causes gsdl2 to signal (by means of the event queue) when the
          # music is done playing. The argument determines the type of event
          # that will be queued.
          # 
          # The event will be queued every time the music finishes, not just the
          # first time. To stop the event from being queued, call this method
          # with no argument.
          #
        gsdl2.mixer.init()
        # Needed so events get pushed
        gsdl2.display.init()
        # Test that we can get the event we expect
        gsdl2.mixer.music.set_endevent(gsdl2.USEREVENT + 1)
        # Some silent data to play - needs to be a wav file, rather than
        # a simple zero pcm file, so SDL's autodetection works
        silent_wav = (b"RIFF\xec\x0d\x00\x00WAVEfmt "
                      b"\x10\x00\x00\x00\x01\x00\x02\x00D\xac"
                      b"\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\xc8\x0d")
        silent_wav += b"\x00" * 3530
        silent = io.BytesIO(silent_wav)
        gsdl2.mixer.music.load(silent)
        # Check we get an event
        gsdl2.mixer.music.play(0)
        # This is a 0.02s sound, but we give a large margin for noise effects
        time.sleep(0.1)
        events = [x for x in gsdl2.event.get() if
                  x.type == gsdl2.USEREVENT + 1]
        self.assertEqual(len(events), 1)
        # Check we only get 1 event despite multiple loops
        gsdl2.mixer.music.play(2)
        # Longer wait because of the loops
        time.sleep(0.3)
        events = [x for x in gsdl2.event.get() if
                  x.type == gsdl2.USEREVENT + 1]
        self.assertEqual(len(events), 1)
        gsdl2.mixer.quit()
        gsdl2.display.quit()

    def todo_test_pause(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.pause:

          # Temporarily stop playback of the music stream. It can be resumed
          # with the gsdl2.mixer.music.unpause() function.
          # 

        self.fail() 

    def todo_test_get_busy(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.get_busy:

          # Returns True when the music stream is actively playing. When the
          # music is idle this returns False.
          # 

        self.fail() 

    def test_get_endevent(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.get_endevent:

          # Returns the event type to be sent every time the music finishes
          # playback. If there is no endevent the function returns
          # gsdl2.NOEVENT.
          # 
        gsdl2.mixer.init()
        # Check set_endevent and get_endevent roundtripping
        gsdl2.mixer.music.set_endevent(gsdl2.USEREVENT + 1)
        self.assertEqual(gsdl2.mixer.music.get_endevent(),
                         gsdl2.USEREVENT + 1)
        # Check that we can set an event outside the SDL event limit,
        # because gsdl2 allows that
        gsdl2.mixer.music.set_endevent(gsdl2.NUMEVENTS + 10)
        self.assertEqual(gsdl2.mixer.music.get_endevent(),
                         gsdl2.NUMEVENTS + 10)
        # Check unsetting
        gsdl2.mixer.music.set_endevent()
        self.assertEqual(gsdl2.mixer.music.get_endevent(),
                         gsdl2.NOEVENT)

        gsdl2.mixer.quit()

    def todo_test_unpause(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.unpause:

          # This will resume the playback of a music stream after it has been paused. 

        self.fail() 

    def todo_test_set_volume(self):

        # __doc__ (as of 2008-08-02) for gsdl2.mixer_music.set_volume:

          # Set the volume of the music playback. The value argument is between
          # 0.0 and 1.0. When new music is loaded the volume is reset.
          # 

        self.fail() 

    def todo_test_set_pos(self):

        # __doc__ (as of 2010-24-05) for gsdl2.mixer_music.set_pos:

          #This sets the position in the music file where playback will start. The
          # meaning of "pos", a float (or a number that can be converted to a float),
          # depends on the music format. Newer versions of SDL_mixer have better
          # positioning support than earlier. An SDLError is raised if a particular
          # format does not support positioning.
          # 

        self.fail() 

if __name__ == '__main__':
    unittest.main()
