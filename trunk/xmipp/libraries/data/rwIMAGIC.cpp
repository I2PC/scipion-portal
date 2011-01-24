/***************************************************************************
 * Authors:     Joaquin Oton (joton@cnb.csic.es)
 *
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/

#include "image_base.h"

/*
 * rwIMAGIC.h
 *
 *  Created on: May 17, 2010
 *      Author: roberto
 */
/*
 Base on rwIMAGIC.h
 Header file for reading and writing Image Science's Imagic files
 Format: 2D image file format for the program Imagic (Image Science)
 Author: Bernard Heymann
 Created: 19990424  Modified: 20011030
*/

#define IMAGICSIZE 1024 // Size of the IMAGIC header for each image

///@defgroup Imagic Imagic File format
///@ingroup ImageFormats

/** Imagic Header
  * @ingroup Imagic
*/
struct IMAGIChead
{             // file header for IMAGIC data
    int imn;          //  0      image location number (1,2,...)
    int ifn;          //  1      # images following, only of importance in the first location
    int ierror;       //  2      error code: error if >0
    int nhfr;         //  3      # header records per image
    int ndate;        //  4      creation day
    int nmonth;       //  5      creation month
    int nyear;        //  6      creation year
    int nhour;        //  7      creation hour
    int nminut;       //  8      creation minute
    int nsec;         //  9      creation second
    int npix2;        // 10      # 4-byte reals in image
    int npixel;       // 11      # image elements
    int ixlp;       // 12      lines per image (Y)
    int iylp;        // 13      pixels per line (X)
    char type[4];      // 14      image type
    int ixold;       // 15      top-left X coordinate
    int iyold;       // 16      top-left Y coordinate
    float avdens;       // 17      average
    float sigma;       // 18      standard deviation
    float varian;       // 19      variance
    float oldavd;      // 20      old average
    float densmax;       // 21      maximum
    float densmin;       // 22      minimum
    //     double sum;       // 23+24  sum of densities
    //     double squares;    // 25+26  sum of squares
    float dummy[4];   // 23-26  dummy place holder
    char lastpr[8];      // 27+28     last program writing file
    char name[80];       // 29-48     image name
    float extra_1[8];   // 49-56     additional parameters
    float eman_alt;   // 57      EMAN: equiv to psi & PFT omega
    float eman_az;    // 58      EMAN: equiv to theta
    float eman_phi;   // 59      EMAN: equiv to phi
    float extra_2[69];   // 60-128     additional parameters
    float euler_alpha;  // 129   Euler angles: psi
    float euler_beta;  // 130       theta
    float euler_gamma;  // 131       phi
    float proj_weight;  // 132   weight of each projection
    float extra_3[66];   // 133-198     additional parameters
    char history[228];      // 199-255   history
} ;

/************************************************************************
@Function: readIMAGIC
@Description:
 Reading an IMAGIC image format.
@Algorithm:
 A 2D file format for the IMAGIC package.
 The header is stored in a separate file with extension ".hed" and
  a fixed size of 1024 bytes per image.
 The image data is stored in a single block in a file with the
  extension ".img".
 Byte order determination: Year and hour values
        must be less than 256*256.
 Data types:     PACK = byte, INTG = short, REAL = float,
        RECO,COMP = complex float.
 Transform type:    Centered (COMP data type)
        RECO is not a transform
 Note that the x and y dimensions are interchanged (actually a display issue).
@Arguments:
 Bimage* p   the image structure.
 int select   image selection in multi-image file (-1 = all images).
@Returns:
 int     error code (<0 means failure).
**************************************************************************/
/** Imagic reader
  * @ingroup Imagic
*/
int  ImageBase::readIMAGIC(int img_select)
{
#undef DEBUG
    //#define DEBUG
#ifdef DEBUG
    printf("DEBUG readIMAGIC: Reading Imagic file\n");
#endif

    IMAGIChead* header = new IMAGIChead;

    if ( fread( header, IMAGICSIZE, 1, fhed ) < 1 )
        REPORT_ERROR(ERR_IO_NOREAD,(std::string)"readIMAGIC: header file of " + filename + " cannot be read");

    // Determine byte order and swap bytes if from little-endian machine
    char*   b = (char *) header;
    int    swap = 0;
    unsigned long i, extent = IMAGICSIZE - 916;  // exclude char bytes from swapping
    if ( ( abs(header->nyear) > SWAPTRIG ) || ( header->ixlp > SWAPTRIG ) )
    {
        swap = 1;
        for ( i=0; i<extent; i+=4 )
            if ( i != 56 )          // exclude type string
                swapbytes(b+i, 4);
    }
    int _xDim,_yDim,_zDim;
    unsigned long int _nDim;
    _xDim = (int) header->iylp;
    _yDim = (int) header->ixlp;
    _zDim = (int) 1;
    _nDim = (unsigned long int) header->ifn + 1 ;

    std::stringstream Num;
    std::stringstream Num2;
    if ( img_select > (int)_nDim )
    {
        Num  << img_select;
        Num2 << _nDim;
        REPORT_ERROR(ERR_INDEX_OUTOFBOUNDS,(std::string)"readImagic: Image number " + Num.str() +
                     " exceeds stack size " + Num2.str());
    }

    if( img_select > -1)
        _nDim=1;

    setDimensions( //setDimensions do not allocate data
        _xDim,
        _yDim,
        _zDim,
        _nDim );

    replaceNsize=_nDim;
    DataType datatype;

    if ( strstr(header->type,"PACK") )
        datatype = UChar;
    else if ( strstr(header->type,"INTG") )
        datatype = Short;
    else if ( strstr(header->type,"REAL") )
        datatype = Float;
    else if ( strstr(header->type,"RECO") )
    {
        datatype = ComplexFloat; // Complex data
        transform = NoTransform;
    }
    else if ( strstr(header->type,"COMP") )
    {
        datatype = ComplexFloat; // Complex transform data
        transform = Centered;
    }

    // Set min-max values and other statistical values
    if ( header->sigma == 0 && header->varian != 0 )
        header->sigma = sqrt(header->varian);
    if ( header->densmax == 0 && header->densmin == 0 && header->sigma != 0 )
    {
        header->densmin = header->avdens - header->sigma;
        header->densmax = header->avdens + header->sigma;
    }

    MDMainHeader.setValue(MDL_MIN,(double)header->densmin);
    MDMainHeader.setValue(MDL_MAX,(double)header->densmax);
    MDMainHeader.setValue(MDL_AVG,(double)header->avdens);
    MDMainHeader.setValue(MDL_STDDEV,(double)header->sigma);
    MDMainHeader.setValue(MDL_SAMPLINGRATEX,(double)1.);
    MDMainHeader.setValue(MDL_SAMPLINGRATEY,(double)1.);
    MDMainHeader.setValue(MDL_SAMPLINGRATEZ,(double)1.);
    MDMainHeader.setValue(MDL_DATATYPE,(int)datatype);


    offset = 0;   // separate header file

    unsigned long   Ndim = _nDim, j = 0;
    if (dataflag<0)   // Don't read the individual header and the data if not necessary
        return 0;

    // View   view;
    char*   hend;

    // Get the header information
    if ( img_select > -1 )
        fseek( fhed, img_select * IMAGICSIZE, SEEK_SET );
    else
        fseek( fhed, 0, SEEK_SET );

    MD.clear();
    MD.resize(Ndim);
    double daux=1.;
    for ( i = 0; i < Ndim; ++i )
    {
        if ( fread( header, IMAGICSIZE, 1, fhed ) < 1 )
            return(-2);
        {
            hend = (char *) header + extent;
            if ( swap )
                for ( b = (char *) header; b<hend; b+=4 )
                    swapbytes(b, 4);

            MD[i].setValue(MDL_ORIGINX,  (double)-1. * header->iyold);
            MD[i].setValue(MDL_ORIGINY,  (double)-1. * header->ixold);
            MD[i].setValue(MDL_ORIGINZ,  zeroD);
            MD[i].setValue(MDL_ANGLEROT, (double)-1. * header->euler_alpha);
            MD[i].setValue(MDL_ANGLETILT,(double)-1. * header->euler_beta);
            MD[i].setValue(MDL_ANGLEPSI, (double)-1. * header->euler_gamma);
            MD[i].setValue(MDL_WEIGHT,   (double)oneD);
            MD[i].setValue(MDL_SCALE, daux);
            j++;
        }
    }

    delete header;

    int pad=0;
    readData(fimg, img_select, datatype, pad );

    return(0);
}

/************************************************************************
@Function: writeIMAGIC
@Description:
 Writing an IMAGIC image format.
@Algorithm:
 A file format for the IMAGIC package.
@Arguments:
 Bimage*    the image structure.
@Returns:
 int     error code (<0 means failure).
**************************************************************************/
/** Imagic Writer
  * @ingroup Imagic
*/
int  ImageBase::writeIMAGIC(int img_select, int mode, std::string bitDepth, bool adjust)
{
#undef DEBUG
    //#define DEBUG
#ifdef DEBUG
    printf("DEBUG writeIMAGIC: Reading Imagic file\n");
#endif

    IMAGIChead* header = new IMAGIChead;
    int Xdim, Ydim, Zdim;
    unsigned long Ndim;
    getDimensions(Xdim, Ydim, Zdim, Ndim);

    // fill in the file header
    header->nhfr = 1;
    header->npix2 = Xdim*Ydim;
    header->npixel = header->npix2;
    header->iylp = Xdim;
    header->ixlp = Ydim;

    header->ifn = Ndim - 1 ;
    header->imn = 1;
    int firtIfn=0;
    if(replaceNsize!=0 && mode == WRITE_APPEND)
    {
        firtIfn     = replaceNsize;
        header->imn = replaceNsize+1;
        header->ifn = 0;//only important in first header
    }

    time_t timer;
    time ( &timer );
    tm* t = localtime(&timer);

    header->ndate = t->tm_mday;
    header->nmonth = t->tm_mon + 1;
    header->nyear = t->tm_year;
    header->nhour = t->tm_hour;
    header->nminut = t->tm_min;
    header->nsec = t->tm_sec;

    unsigned long   imgStart=0;
    if (img_select != -1)
        imgStart=img_select;
    if (mode = WRITE_APPEND)
        imgStart=0;


    // Cast T to datatype without convert data
    DataType wDType,myTypeID = myT();
    CastWriteMode castMode;

    if (bitDepth == "")
    {
        castMode = CAST;
        switch(myTypeID)
        {
        case Double:
        case Float:
        case Int:
        case UInt:
            wDType = Float;
            strcpy(header->type,"REAL");
            break;
        case UShort:
            castMode = CONVERT;
        case Short:
            wDType = Short;
            strcpy(header->type,"INTG");
            break;
        case SChar:
            castMode = CONVERT;
        case UChar:
            wDType = UChar;
            strcpy(header->type,"PACK");
            break;
        case ComplexFloat:
        case ComplexDouble:
            wDType = ComplexFloat;
            strcpy(header->type,"COMP");
            break;
        default:
            wDType = Unknown_Type;
            REPORT_ERROR(ERR_TYPE_INCORRECT,(std::string)"ERROR: Unsupported data type by IMAGIC format.");
        }
    }
    else //Convert to other data type
    {
        // Default Value
        wDType = (bitDepth == "default") ? Float : datatypeRAW(bitDepth);

        switch (wDType)
        {
        case UChar:
            strcpy(header->type,"PACK");
            break;
        case Short:
            strcpy(header->type,"INTG");
            break;
        case Float:
            strcpy(header->type,"REAL");
            break;
        case ComplexFloat:
            strcpy(header->type,"COMP");
            break;
        default:
            REPORT_ERROR(ERR_TYPE_INCORRECT,"ERROR: incorrect IMAGIC bits depth value.");
        }
        castMode = (adjust)? ADJUST : CONVERT;
    }

    size_t datasize, datasize_n;
    datasize_n = (size_t)Xdim*Ydim*Zdim;
    datasize = datasize_n * gettypesize(wDType);

    double aux;

    if (!MDMainHeader.empty())
    {

        if(MDMainHeader.getValue(MDL_MIN,   aux))
            header->densmin = (float)aux;
        if(MDMainHeader.getValue(MDL_MAX,   aux))
            header->densmax = (float)aux;
        if(MDMainHeader.getValue(MDL_AVG,   aux))
            header->avdens   = (float)aux;
        if(MDMainHeader.getValue(MDL_STDDEV,aux))
        {
            header->sigma  = (float)aux;
            header->varian = (float)(aux*aux);
        }
    }

    memcpy(header->lastpr, "Xmipp", 5);
    memcpy(header->name, filename.c_str(), 80);

    /*
     * BLOCK HEADER IF NEEDED
     */
    struct flock fl;

    fl.l_type   = F_WRLCK;  /* F_RDLCK, F_WRLCK, F_UNLCK    */
    fl.l_whence = SEEK_SET; /* SEEK_SET, SEEK_CUR, SEEK_END */
    fl.l_start  = 0;        /* Offset from l_whence         */
    fl.l_len    = 0;        /* length, 0 = to EOF           */
    fl.l_pid    = getpid(); /* our PID                      */
    fcntl(fileno(fimg),       F_SETLKW, &fl); /* locked */
    fcntl(fileno(fhed), F_SETLKW, &fl); /* locked */

    if(mode==WRITE_APPEND)
    {
        if(replaceNsize!=0)
        {   //rewrite firt record
            fseek( fhed, sizeof(int), SEEK_SET);
            fwrite(&firtIfn,SIZEOF_INT,1,fhed);
        }
        fseek( fhed, 0, SEEK_END);
        fseek( fimg, 0, SEEK_END);
    }
    else if(mode==WRITE_REPLACE)
    {
        fseek( fimg, datasize   * img_select, SEEK_SET);
        fseek( fhed, IMAGICSIZE * img_select, SEEK_SET);
    }
    else //mode==WRITE_OVERWRITE
    {
        //this is already done in image.h but only for the data file not for the header
        //fseek( fimg, 0, SEEK_SET);
        fseek( fhed, 0, SEEK_SET);
    }

    if (mmapOnWrite)
        REPORT_ERROR(ERR_NOT_IMPLEMENTED,"To be implemented");


    i = imgStart;
    for (std::vector<MDRow>::iterator it = MD.begin(); it != MD.end(); ++it)
    {
        header->iyold=header->ixold=header->euler_alpha=header->euler_beta=header->euler_gamma=0.;
        if(it->getValue(MDL_ORIGINX,  aux))
            header->iyold  = (float)-aux;
        if(it->getValue(MDL_ORIGINY,  aux))
            header->ixold  =(float)-aux;
        //if(it->getValue(MDL_ORIGINZ,  aux))
        //    header->zoff  =(float)aux;
        if(it->getValue(MDL_ANGLEROT, aux))
            header->euler_alpha   =(float)-aux;
        if(it->getValue(MDL_ANGLETILT,aux))
            header->euler_beta    =(float)-aux;
        if(it->getValue(MDL_ANGLEPSI, aux))
            header->euler_gamma =(float)-aux;

        fwrite( header, IMAGICSIZE, 1, fhed );
        writeData(fimg, i*datasize_n, wDType, datasize_n, castMode);

        ++i;
    }

    //Unlock
    fl.l_type   = F_UNLCK;
    fcntl(fileno(fimg), F_SETLK, &fl); /* unlocked */
    fcntl(fileno(fhed), F_SETLK, &fl); /* unlocked */

    delete header;

    return(0);
}
