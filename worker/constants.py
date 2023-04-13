FIREFOX_SETTINGS = {
        "pdfjs.disabled": False,
        "browser.taskbar.lists.enabled": True,
        "browser.taskbar.lists.frequent.enabled": True,
        "browser.taskbar.lists.recent.enabled": True,
        "browser.taskbar.lists.tasks.enabled": True,
        "browser.taskbar.lists.maxListItemCount": 10,
}


SPOOF_FINGERPRINT = '''
    (() => {
        delete navigator.__proto__.webdriver;
        Object.defineProperty(navigator, 'deviceMemory', { value: %d, configurable: true });

        const originalHardwareConcurrency = navigator.hardwareConcurrency;
        const originalPropertyDescriptor = Object.getOwnPropertyDescriptor(
            Navigator.prototype, 'hardwareConcurrency'
        );
        Object.defineProperty(Navigator.prototype, 'hardwareConcurrency', {
            get: function() {
                return %d;
            },
            enumerable: originalPropertyDescriptor.enumerable,
            configurable: originalPropertyDescriptor.configurable,
        });

        const originalWorker = window.Worker;
        window.Worker = new Proxy(originalWorker, {
            construct(target, args) {
                const worker = new target(...args);
                const handleMessage = (event) => {
                    if (event.data === 'spoofHardwareConcurrency') {
                        worker.postMessage(navigator.hardwareConcurrency);
                    }
                };
                worker.addEventListener('message', handleMessage);
                return worker;
            }
        });
    })();
'''
