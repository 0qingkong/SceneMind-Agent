import type { DetectedRelation } from '../types/api'

function reciprocalKey(relation: DetectedRelation) {
  const { subject_id: subjectId, object_id: objectId, predicate } = relation
  switch (predicate) {
    case 'left_of':
      return `horizontal:${subjectId}:${objectId}`
    case 'right_of':
      return `horizontal:${objectId}:${subjectId}`
    case 'above':
      return `vertical:${subjectId}:${objectId}`
    case 'below':
      return `vertical:${objectId}:${subjectId}`
    case 'inside':
      return `containment:${subjectId}:${objectId}`
    case 'contains':
      return `containment:${objectId}:${subjectId}`
    case 'near':
    case 'overlaps': {
      const [firstId, secondId] = [subjectId, objectId].sort()
      return `${predicate}:${firstId}:${secondId}`
    }
  }
}

export function collapseReciprocalRelations(
  relations: readonly DetectedRelation[],
) {
  const seen = new Set<string>()
  return relations.filter((relation) => {
    const key = reciprocalKey(relation)
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}
