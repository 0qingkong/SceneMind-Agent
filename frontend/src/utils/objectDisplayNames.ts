import type { DetectedObject } from '../types/api'

export type DisplayNameObject = Pick<
  DetectedObject,
  'id' | 'label' | 'display_name'
> & { sort_order?: number }

function baseDisplayName(item: DisplayNameObject) {
  return item.label.toLowerCase() === 'person' ? '人物' : item.display_name
}

export function buildObjectDisplayNameMap(
  objects: readonly DisplayNameObject[],
): Map<string, string> {
  const ordered = objects
    .map((item, index) => ({ item, index }))
    .sort(
      (first, second) =>
        (first.item.sort_order ?? first.index) -
          (second.item.sort_order ?? second.index) || first.index - second.index,
    )
  const totals = new Map<string, number>()
  for (const { item } of ordered) {
    const name = baseDisplayName(item)
    totals.set(name, (totals.get(name) ?? 0) + 1)
  }

  const ordinals = new Map<string, number>()
  const names = new Map<string, string>()
  for (const { item } of ordered) {
    const name = baseDisplayName(item)
    if ((totals.get(name) ?? 0) === 1) {
      names.set(item.id, name)
      continue
    }
    const ordinal = (ordinals.get(name) ?? 0) + 1
    ordinals.set(name, ordinal)
    names.set(item.id, `${name} ${ordinal}`)
  }
  return names
}

export function objectDisplayName(
  names: ReadonlyMap<string, string>,
  objectId: string,
) {
  return names.get(objectId) ?? `未知物体（${objectId}）`
}
