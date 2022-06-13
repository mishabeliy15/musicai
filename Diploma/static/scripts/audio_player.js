/** Implementation of the presentation of the audio player */
import lottieWeb from 'https://cdn.skypack.dev/lottie-web';

let audioPlayerContainers = document.getElementsByClassName('audio-player-container');

for(let audioPlayerContainer of audioPlayerContainers) {
    audioPlayerContainer.playIconContainer = audioPlayerContainer.querySelector('#play-icon');
    audioPlayerContainer.seekSlider = audioPlayerContainer.querySelector('#seek-slider');
	audioPlayerContainer.audio = audioPlayerContainer.querySelector('audio');
    audioPlayerContainer.timeContainer = audioPlayerContainer.querySelector('#time');
    audioPlayerContainer.raf = null;
    audioPlayerContainer.playState = 'play';

    audioPlayerContainer.playAnimation = lottieWeb.loadAnimation({
        container: audioPlayerContainer.playIconContainer,
        path: 'https://maxst.icons8.com/vue-static/landings/animated-icons/icons/pause/pause.json',
        renderer: 'svg',
        loop: false,
        autoplay: false,
        name: "Play Animation",
    });

    audioPlayerContainer.playAnimation.goToAndStop(14, true);

    audioPlayerContainer.playIconContainer.addEventListener('click', () => {
        if (audioPlayerContainer.playState === 'play') {
            audioPlayerContainer.audio.play();
            audioPlayerContainer.playAnimation.playSegments([14, 27], true);
            requestAnimationFrame(whilePlaying);
            audioPlayerContainer.playState = 'pause';

			if(document.currentAudioPlayer != null) {
				pauseAudio(document.currentAudioPlayer);
			}

			document.currentAudioPlayer = audioPlayerContainer;
			audioPlayerContainer.setAttribute("playing", true);
        } else {
			pauseAudio(audioPlayerContainer);
        }
    });

	const pauseAudio = (player) => {
		player.audio.pause();
		player.playAnimation.playSegments([0, 14], true);
		cancelAnimationFrame(player.raf);
		player.playState = 'play';

		document.currentAudioPlayer = null;
		player.setAttribute("playing", false);
	}

    const showRangeProgress = (rangeInput) => {
        audioPlayerContainer.style.setProperty('--seek-before-width', rangeInput.value / rangeInput.max * 100 + '%');
    }

    audioPlayerContainer.seekSlider.addEventListener('input', (e) => {
        showRangeProgress(e.target);
    });

    /** Implementation of the functionality of the audio player */

    const calculateTime = (secs) => {
        const minutes = Math.floor(secs / 60);
        const seconds = Math.floor(secs % 60);
        const returnedSeconds = seconds < 10 ? `0${seconds}` : `${seconds}`;
        return `${minutes}:${returnedSeconds}`;
    }

    const displayTime = () => {
		audioPlayerContainer.timeContainer.textContent = calculateTime(audioPlayerContainer.seekSlider.value) + " / " + calculateTime(audioPlayerContainer.audio.duration);
    }

    const setSliderMax = () => {
        audioPlayerContainer.seekSlider.max = Math.floor(audioPlayerContainer.audio.duration);
    }

    const displayBufferedAmount = () => {
        const bufferedAmount = Math.floor(audioPlayerContainer.audio.buffered.end(audioPlayerContainer.audio.buffered.length - 1));
        audioPlayerContainer.style.setProperty('--buffered-width', `${(bufferedAmount / audioPlayerContainer.seekSlider.max) * 100}%`);
    }

    const whilePlaying = () => {
        audioPlayerContainer.seekSlider.value = Math.floor(audioPlayerContainer.audio.currentTime);
		displayTime()
        audioPlayerContainer.style.setProperty('--seek-before-width', `${audioPlayerContainer.seekSlider.value / audioPlayerContainer.seekSlider.max * 100}%`);
        audioPlayerContainer.raf = requestAnimationFrame(whilePlaying);
    }

    if (audioPlayerContainer.audio.readyState > 0) {
        displayTime();
        setSliderMax();
        displayBufferedAmount();
    } else {
        audioPlayerContainer.audio.addEventListener('loadedmetadata', () => {
            displayTime();
            setSliderMax();
            displayBufferedAmount();
        });
    }

    audioPlayerContainer.audio.addEventListener('progress', displayBufferedAmount);

    audioPlayerContainer.seekSlider.addEventListener('input', () => {
		displayTime();
        if (!audioPlayerContainer.audio.paused) {
            cancelAnimationFrame(audioPlayerContainer.raf);
        }
    });

    audioPlayerContainer.seekSlider.addEventListener('change', () => {
        audioPlayerContainer.audio.currentTime = parseFloat(audioPlayerContainer.seekSlider.value);
        if (!audioPlayerContainer.audio.paused) {
            requestAnimationFrame(whilePlaying);
        }
    });
}