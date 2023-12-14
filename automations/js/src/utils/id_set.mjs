/**
 * An ID set is a set that can uniquely store objects, something a regular `Set`
 * cannot do, by using their `id` field as the unique identifier. Ironically, it
 * does this by storing the IDs in a regular `Set` under the hood.
 */
export class IdSet {
  constructor() {
    this.items = []
    this.ids = new Set()
  }

  /**
   * Add an item to the set. The item must have an `id` field.
   * @param item {object | {id: string}} the item to add
   */
  add(item) {
    if (!this.ids.has(item.id)) {
      this.items.push(item)
      this.ids.add(item.id)
    }
  }

  /**
   * Check if the set contains the given item.
   * @param item {object | {id: string}} the item to check
   * @returns {boolean} whether the set contains the item
   */
  has(item) {
    return this.ids.has(item.id)
  }
}
