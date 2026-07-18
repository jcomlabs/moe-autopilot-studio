import '@testing-library/jest-dom/vitest'

class ResizeObserverStub {
  private readonly callback: ResizeObserverCallback

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback
  }

  observe(target: Element) {
    this.callback([{
      target,
      contentRect: { x: 0, y: 0, width: 800, height: 300, top: 0, right: 800, bottom: 300, left: 0, toJSON: () => ({}) },
      borderBoxSize: [], contentBoxSize: [], devicePixelContentBoxSize: [],
    }], this as unknown as ResizeObserver)
  }
  unobserve() {}
  disconnect() {}
}

Object.defineProperty(globalThis, 'ResizeObserver', {
  value: ResizeObserverStub,
  writable: true,
})
