declare module 'react-split-pane' {
  import * as React from 'react'
  export interface SplitPaneProps {
    split?: 'vertical' | 'horizontal'
    minSize?: number
    maxSize?: number
    defaultSize?: number | string
    primary?: 'first' | 'second'
    className?: string
    style?: React.CSSProperties
    onDragFinished?: () => void
    onChange?: (size: number) => void
    allowResize?: boolean
    children?: React.ReactNode
  }
  export default class SplitPane extends React.Component<SplitPaneProps> {}
}

