node ('master') {
    stage ('Checkout') {
        checkoutSubmodule()
    }

    stage ('Pre-commit Checks') {
        preCommit()
    }

    stage ('Build') {
        buildGenericPkg()
    }

    stage ('Test') {
        checkSymLinks()
        shellcheck()
        try {
            lintian()
        } catch (e) {
            currentBuild.result = 'UNSTABLE'
        }
    }

    stage ('Publish') {
        publishSirius()
    }
}
