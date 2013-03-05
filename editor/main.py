import sys, os
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )

import view
import presenter


if __name__ == '__main__':
    presenter = presenter.Presenter()

    view = view.View()
    view.SetPresenter(presenter)

    presenter.SetView(view)
    if len(sys.argv) >= 2:
        presenter.LoadFile(sys.argv[1])

    sys.exit( presenter.Exec() )
