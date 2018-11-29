node ('master') {
    stage ('Checkout') {
        checkoutSubmodule()
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
