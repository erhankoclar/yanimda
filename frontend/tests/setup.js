import { afterEach, beforeEach } from 'vitest'

import { restoreApi } from './helpers/fakeApi'

// Her test varsayılan sahte API ile başlar ve temiz bir localStorage ile biter.
beforeEach(() => restoreApi())
afterEach(() => window.localStorage.clear())
