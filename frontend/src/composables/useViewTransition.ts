type ViewTransitionDocument = Document & { startViewTransition?: (update: () => void | Promise<void>) => unknown }

export function useViewTransition() {
  const runTransition = async (update: () => void | Promise<void>) => {
    const documentWithTransition = document as ViewTransitionDocument
    if (documentWithTransition.startViewTransition) {
      documentWithTransition.startViewTransition(update)
      return
    }
    await update()
  }

  return { runTransition }
}
